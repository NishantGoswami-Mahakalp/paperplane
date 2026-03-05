# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
import factory
from uuid import uuid4
from django.utils import timezone

from plane.db.models import (
    User,
    Workspace,
    Project,
    ProjectMember,
    ApprovalPolicy,
    ApprovalPolicyApprover,
    ApprovalDecision,
)
from plane.app.serializers.approval import (
    ApprovalPolicySerializer,
    ApprovalDecisionSerializer,
    ApprovalApproveSerializer,
    ApprovalRejectSerializer,
    ApprovalReassignSerializer,
)


class ApprovalUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: f"approval-user{n}@plane.so")
    password = factory.PostGenerationMethodCall("set_password", "password")
    first_name = factory.Sequence(lambda n: f"First{n}")
    last_name = factory.Sequence(lambda n: f"Last{n}")
    is_active = True


class ApprovalWorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workspace
        django_get_or_create = ("slug",)

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Approval Workspace {n}")
    slug = factory.Sequence(lambda n: f"approval-workspace-{n}")
    owner = factory.SubFactory(ApprovalUserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class ApprovalProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        django_get_or_create = ("name", "workspace")

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Approval Project {n}")
    workspace = factory.SubFactory(ApprovalWorkspaceFactory)
    created_by = factory.SelfAttribute("workspace.owner")
    updated_by = factory.SelfAttribute("workspace.owner")


@pytest.mark.unit
class TestApprovalPolicySerializer:
    def test_approval_policy_serializer_fields(self, db):
        user = ApprovalUserFactory.create(email="policy-test@example.com")
        workspace = ApprovalWorkspaceFactory.create(slug="policy-test-ws", owner=user)
        project = ApprovalProjectFactory.create(name="Policy Test Project", workspace=workspace)

        policy = ApprovalPolicy.objects.create(
            name="Test Policy",
            description="Test Description",
            project=project,
            workspace=workspace,
            type=ApprovalPolicy.Type.SEQUENTIAL,
            required_count=1,
            is_active=True,
        )

        serialized_data = ApprovalPolicySerializer(policy).data

        assert "id" in serialized_data
        assert serialized_data["name"] == "Test Policy"
        assert serialized_data["description"] == "Test Description"
        assert serialized_data["type"] == "sequential"
        assert serialized_data["required_count"] == 1
        assert serialized_data["is_active"] is True


@pytest.mark.unit
class TestApprovalDecisionSerializer:
    def test_approval_decision_serializer_fields(self, db):
        user = ApprovalUserFactory.create(email="decision-test@example.com")
        workspace = ApprovalWorkspaceFactory.create(slug="decision-test-ws", owner=user)
        project = ApprovalProjectFactory.create(name="Decision Test Project", workspace=workspace)

        policy = ApprovalPolicy.objects.create(
            name="Decision Policy",
            project=project,
            workspace=workspace,
            type=ApprovalPolicy.Type.PARALLEL,
            required_count=2,
            is_active=True,
        )

        item_id = uuid4()
        decision = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.PENDING,
            order=0,
        )

        serialized_data = ApprovalDecisionSerializer(decision).data

        assert "id" in serialized_data
        assert serialized_data["item_id"] == str(item_id)
        assert serialized_data["status"] == "pending"
        assert serialized_data["order"] == 0


@pytest.mark.unit
class TestApprovalApproveSerializer:
    def test_approve_serializer_valid_without_comment(self, db):
        data = {}
        serializer = ApprovalApproveSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get("comment") == ""

    def test_approve_serializer_valid_with_comment(self, db):
        data = {"comment": "Looks good!"}
        serializer = ApprovalApproveSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get("comment") == "Looks good!"


@pytest.mark.unit
class TestApprovalRejectSerializer:
    def test_reject_serializer_valid_with_comment(self, db):
        data = {"comment": "Needs changes"}
        serializer = ApprovalRejectSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get("comment") == "Needs changes"

    def test_reject_serializer_invalid_without_comment(self, db):
        data = {}
        serializer = ApprovalRejectSerializer(data=data)
        assert not serializer.is_valid()
        assert "comment" in serializer.errors


@pytest.mark.unit
class TestApprovalReassignSerializer:
    def test_reassign_serializer_valid(self, db):
        data = {"approver_id": str(uuid4())}
        serializer = ApprovalReassignSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get("approver_id") == data["approver_id"]

    def test_reassign_serializer_invalid_without_approver_id(self, db):
        data = {}
        serializer = ApprovalReassignSerializer(data=data)
        assert not serializer.is_valid()
        assert "approver_id" in serializer.errors


@pytest.mark.unit
class TestSequentialApprovalEnforcement:
    def test_sequential_order_enforcement(self, db):
        user = ApprovalUserFactory.create(email="sequential-test@example.com")
        workspace = ApprovalWorkspaceFactory.create(slug="sequential-test-ws", owner=user)
        project = ApprovalProjectFactory.create(name="Sequential Test Project", workspace=workspace)

        policy = ApprovalPolicy.objects.create(
            name="Sequential Policy",
            project=project,
            workspace=workspace,
            type=ApprovalPolicy.Type.SEQUENTIAL,
            required_count=1,
            is_active=True,
        )

        item_id = uuid4()

        decision1 = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.PENDING,
            order=0,
        )

        decision2 = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.PENDING,
            order=1,
        )

        decision1.status = ApprovalDecision.Status.APPROVED
        decision1.save()

        approved_count = ApprovalDecision.objects.filter(
            policy=policy,
            item_id=item_id,
            status=ApprovalDecision.Status.APPROVED,
            deleted_at__isnull=True,
        ).count()

        assert approved_count == 1

        previous_decisions = ApprovalDecision.objects.filter(
            policy=policy,
            item_id=item_id,
            order__lt=decision2.order,
            deleted_at__isnull=True,
        ).exclude(status=ApprovalDecision.Status.APPROVED)

        assert not previous_decisions.exists()


@pytest.mark.unit
class TestParallelApprovalEnforcement:
    def test_parallel_required_count_enforcement(self, db):
        user = ApprovalUserFactory.create(email="parallel-test@example.com")
        workspace = ApprovalWorkspaceFactory.create(slug="parallel-test-ws", owner=user)
        project = ApprovalProjectFactory.create(name="Parallel Test Project", workspace=workspace)

        policy = ApprovalPolicy.objects.create(
            name="Parallel Policy",
            project=project,
            workspace=workspace,
            type=ApprovalPolicy.Type.PARALLEL,
            required_count=2,
            is_active=True,
        )

        item_id = uuid4()

        decision1 = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.APPROVED,
            order=0,
        )

        decision2 = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.APPROVED,
            order=1,
        )

        decision3 = ApprovalDecision.objects.create(
            policy=policy,
            item_id=item_id,
            requested_by=user,
            approver=user,
            status=ApprovalDecision.Status.PENDING,
            order=2,
        )

        approved_count = ApprovalDecision.objects.filter(
            policy=policy,
            item_id=item_id,
            status=ApprovalDecision.Status.APPROVED,
            deleted_at__isnull=True,
        ).count()

        max_approvals = policy.required_count

        assert approved_count >= max_approvals
