# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ROLE, allow_permission
from plane.app.serializers.approval import (
    ApprovalDecisionSerializer,
    ApprovalPolicySerializer,
    ApprovalApproveSerializer,
    ApprovalRejectSerializer,
    ApprovalReassignSerializer,
)
from plane.db.models import (
    ApprovalDecision,
    ApprovalPolicy,
    ApprovalPolicyApprover,
    Issue,
    ProjectMember,
    User,
)

from .. import BaseAPIView, BaseViewSet


class ApprovalPolicyViewSet(BaseViewSet):
    model = ApprovalPolicy
    serializer_class = ApprovalPolicySerializer

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def list(self, request, slug, project_id):
        policies = ApprovalPolicy.objects.filter(
            workspace__slug=slug,
            project_id=project_id,
            is_active=True,
        ).prefetch_related("policy_approvers", "policy_approvers__approver")
        serializer = self.get_serializer(policies, many=True)
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN])
    def create(self, request, slug, project_id):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN])
    def partial_update(self, request, slug, project_id, pk):
        policy = self.get_object()
        serializer = self.get_serializer(policy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, project_id, pk):
        policy = self.get_object()
        policy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApprovalDecisionViewSet(BaseViewSet):
    model = ApprovalDecision
    serializer_class = ApprovalDecisionSerializer

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def list(self, request, slug, project_id, item_id):
        decisions = ApprovalDecision.objects.filter(
            policy__workspace__slug=slug,
            policy__project_id=project_id,
            item_id=item_id,
        ).select_related("policy", "requested_by", "approver")
        serializer = ApprovalDecisionSerializer(decisions, many=True)
        return Response(serializer.data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def retrieve(self, request, slug, project_id, item_id, pk):
        decision = self.get_object()
        serializer = ApprovalDecisionSerializer(decision)
        return Response(serializer.data)


class ApprovalRequestEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, item_id):
        issue = Issue.objects.get(
            workspace__slug=slug,
            project_id=project_id,
            pk=item_id,
        )

        policy_id = request.data.get("policy_id")
        if not policy_id:
            return Response(
                {"error": "policy_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            policy = ApprovalPolicy.objects.get(
                pk=policy_id,
                project_id=project_id,
                is_active=True,
            )
        except ApprovalPolicy.DoesNotExist:
            return Response(
                {"error": "Approval policy not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        existing = ApprovalDecision.objects.filter(
            policy=policy,
            item_id=item_id,
            deleted_at__isnull=True,
        ).exists()
        if existing:
            return Response(
                {"error": "Approval request already exists for this item"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approvers = ApprovalPolicyApprover.objects.filter(
            policy=policy,
        ).order_by("order")

        if not approvers.exists():
            return Response(
                {"error": "Policy has no approvers configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decisions_created = []
        for approver in approvers:
            decision = ApprovalDecision.objects.create(
                policy=policy,
                item_id=item_id,
                requested_by=request.user,
                approver=approver.approver,
                status=ApprovalDecision.Status.PENDING,
                order=approver.order,
            )
            decisions_created.append(decision)

        serializer = ApprovalDecisionSerializer(decisions_created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApprovalActionEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def get_approval_decision(self, item_id, approval_id, slug, project_id):
        try:
            return ApprovalDecision.objects.get(
                pk=approval_id,
                policy__workspace__slug=slug,
                policy__project_id=project_id,
                item_id=item_id,
            )
        except ApprovalDecision.DoesNotExist:
            return None

    def can_approve_reject(self, decision, user, project_id, slug):
        if decision.approver_id != user.id:
            return False, "You are not the assigned approver for this decision"

        if decision.status != ApprovalDecision.Status.PENDING:
            return False, "This decision has already been processed"

        policy = decision.policy

        if policy.type == ApprovalPolicy.Type.SEQUENTIAL:
            previous_decisions = ApprovalDecision.objects.filter(
                policy=policy,
                item_id=decision.item_id,
                order__lt=decision.order,
                deleted_at__isnull=True,
            ).exclude(status=ApprovalDecision.Status.APPROVED)

            if previous_decisions.exists():
                return False, "Previous approval decisions must be approved first"

        elif policy.type == ApprovalPolicy.Type.PARALLEL:
            approved_count = ApprovalDecision.objects.filter(
                policy=policy,
                item_id=decision.item_id,
                status=ApprovalDecision.Status.APPROVED,
                deleted_at__isnull=True,
            ).count()

            if decision.status == ApprovalDecision.Status.PENDING:
                max_approvals = policy.required_count
                if approved_count >= max_approvals:
                    return False, f"Required number of approvals ({max_approvals}) already reached"

        return True, None

    def can_reassign(self, decision, user, project_id, slug):
        if decision.status != ApprovalDecision.Status.PENDING:
            return False, "Can only reassign pending decisions"

        is_requester = decision.requested_by_id == user.id
        is_admin = ProjectMember.objects.filter(
            workspace__slug=slug,
            project_id=project_id,
            member=user,
            role=ROLE.ADMIN.value,
        ).exists()

        if not is_requester and not is_admin:
            return False, "Only the requester or admin can reassign"

        return True, None


class ApprovalApproveEndpoint(ApprovalActionEndpoint):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def post(self, request, slug, project_id, item_id, approval_id):
        decision = self.get_approval_decision(item_id, approval_id, slug, project_id)
        if not decision:
            return Response(
                {"error": "Approval decision not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        can_act, error_message = self.can_approve_reject(decision, request.user, project_id, slug)
        if not can_act:
            return Response(
                {"error": error_message},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApprovalApproveSerializer(data=request.data)
        if serializer.is_valid():
            decision.approver = request.user
            decision.status = ApprovalDecision.Status.APPROVED
            decision.comment = serializer.validated_data.get("comment", "")
            decision.save()

            output_serializer = ApprovalDecisionSerializer(decision)
            return Response(output_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovalRejectEndpoint(ApprovalActionEndpoint):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def post(self, request, slug, project_id, item_id, approval_id):
        decision = self.get_approval_decision(item_id, approval_id, slug, project_id)
        if not decision:
            return Response(
                {"error": "Approval decision not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        can_act, error_message = self.can_approve_reject(decision, request.user, project_id, slug)
        if not can_act:
            return Response(
                {"error": error_message},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApprovalRejectSerializer(data=request.data)
        if serializer.is_valid():
            decision.approver = request.user
            decision.status = ApprovalDecision.Status.REJECTED
            decision.comment = serializer.validated_data.get("comment", "")
            decision.save()

            output_serializer = ApprovalDecisionSerializer(decision)
            return Response(output_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovalReassignEndpoint(ApprovalActionEndpoint):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, item_id, approval_id):
        decision = self.get_approval_decision(item_id, approval_id, slug, project_id)
        if not decision:
            return Response(
                {"error": "Approval decision not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        can_act, error_message = self.can_reassign(decision, request.user, project_id, slug)
        if not can_act:
            return Response(
                {"error": error_message},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApprovalReassignSerializer(data=request.data)
        if serializer.is_valid():
            new_approver_id = serializer.validated_data.get("approver_id")
            try:
                new_approver = User.objects.get(pk=new_approver_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "New approver user not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            is_project_member = ProjectMember.objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                member=new_approver,
            ).exists()

            if not is_project_member:
                return Response(
                    {"error": "New approver must be a project member"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            decision.approver = new_approver
            decision.save()

            output_serializer = ApprovalDecisionSerializer(decision)
            return Response(output_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
