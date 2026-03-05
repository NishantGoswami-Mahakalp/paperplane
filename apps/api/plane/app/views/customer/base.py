# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db.models import Value, UUIDField

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ROLE, allow_permission
from plane.app.views.base import BaseViewSet
from plane.db.models import Customer, CustomerContact, Issue, StateGroup
from plane.app.serializers import (
    CustomerSerializer,
    CustomerLiteSerializer,
    CustomerListSerializer,
    CustomerContactSerializer,
)
from plane.utils.filters import filter_by_health_score


class CustomerViewSet(BaseViewSet):
    model = Customer
    serializer_class = CustomerSerializer
    permission_classes = []

    filterset_fields = ["status", "tags"]
    search_fields = ["name", "email", "description"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("workspace")
            .prefetch_related("contacts", "tags")
            .annotate(
                issue_count=Count("issues", filter=Q(issues__deleted_at__isnull=True)),
                open_issue_count=Count(
                    "issues",
                    filter=Q(
                        issues__deleted_at__isnull=True,
                        issues__state__group__in=[
                            StateGroup.BACKLOG.value,
                            StateGroup.UNSTARTED.value,
                            StateGroup.STARTED.value,
                        ],
                    ),
                ),
                closed_issue_count=Count(
                    "issues",
                    filter=Q(
                        issues__deleted_at__isnull=True,
                        issues__state__group=StateGroup.COMPLETED.value,
                    ),
                ),
            )
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def list(self, request, slug):
        queryset = self.get_queryset()

        status_filter = request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        health_score = request.GET.get("health_score")
        if health_score:
            queryset = filter_by_health_score(queryset, health_score)

        return self.paginate(
            request=request,
            queryset=queryset,
            on_results=lambda customers: CustomerSerializer(customers, many=True).data,
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def create(self, request, slug):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace_id=self.kwargs.get("workspace_id"))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def retrieve(self, request, slug, pk):
        customer = self.get_object()
        return Response(CustomerSerializer(customer).data)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def partial_update(self, request, slug, pk):
        customer = self.get_object()
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, pk):
        customer = self.get_object()
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerContactViewSet(BaseViewSet):
    model = CustomerContact
    serializer_class = CustomerContactSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(customer__workspace__slug=self.kwargs.get("slug"), customer_id=self.kwargs.get("customer_id"))
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def list(self, request, slug, customer_id):
        contacts = self.get_queryset()
        return self.paginate(
            request=request,
            queryset=contacts,
            on_results=lambda contacts: CustomerContactSerializer(contacts, many=True).data,
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def create(self, request, slug, customer_id):
        serializer = CustomerContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer_id=customer_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def partial_update(self, request, slug, customer_id, pk):
        contact = self.get_object()
        serializer = CustomerContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @allow_permission([ROLE.ADMIN])
    def destroy(self, request, slug, customer_id, pk):
        contact = self.get_object()
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerIssuesViewSet(BaseViewSet):
    model = Issue
    serializer_class = None

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def list(self, request, slug, customer_id):
        from plane.app.serializers import IssueDetailSerializer
        from plane.db.models import State, FileAsset, IssueLink, CycleIssue
        from django.db.models import OuterRef, Func, F

        customer = Customer.objects.get(pk=customer_id, workspace__slug=slug)

        issues = (
            Issue.objects.filter(customer=customer, workspace__slug=slug)
            .select_related("workspace", "project", "state", "parent", "type")
            .prefetch_related("assignees", "labels")
            .annotate(
                cycle_id=OuterRef(
                    CycleIssue.objects.filter(issue=OuterRef("id"), deleted_at__isnull=True).values("cycle_id")[:1]
                )
            )
            .annotate(
                link_count=IssueLink.objects.filter(issue=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                attachment_count=FileAsset.objects.filter(
                    issue_id=OuterRef("id"),
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                label_ids=Coalesce(
                    ArrayAgg(
                        "labels__id",
                        distinct=True,
                        filter=Q(~Q(labels__id__isnull=True) & Q(label_issue__deleted_at__isnull=True)),
                    ),
                    Value([], output_field=ArrayField(UUIDField())),
                ),
                assignee_ids=Coalesce(
                    ArrayAgg(
                        "assignees__id",
                        distinct=True,
                        filter=Q(
                            ~Q(assignees__id__isnull=True)
                            & Q(assignees__member_project__is_active=True)
                            & Q(issue_assignee__deleted_at__isnull=True)
                        ),
                    ),
                    Value([], output_field=ArrayField(UUIDField())),
                ),
            )
        )

        order_by = request.GET.get("order_by", "-created_at")
        issues = issues.order_by(order_by)

        state_group = request.GET.get("state_group")
        if state_group:
            issues = issues.filter(state__group=state_group)

        return self.paginate(
            request=request,
            queryset=issues,
            on_results=lambda issue_list: IssueDetailSerializer(issue_list, many=True).data,
        )
