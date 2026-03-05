# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db.models import Q

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.db.models import Customer, CustomerContact, CustomerComment, IntakeIssue, Issue
from plane.api.serializers import (
    CustomerSerializer,
    CustomerContactSerializer,
    CustomerLiteSerializer,
    CustomerCommentSerializer,
)
from .base import BaseAPIView
from plane.utils.paginator import BasePaginator


class CustomerListCreateAPIEndpoint(BaseAPIView, BasePaginator):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            deleted_at__isnull=True,
        ).select_related("workspace")

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search) | Q(company__icontains=search)
            )

        return queryset

    def get(self, request, slug):
        customers = self.get_queryset()
        customers = self.filter_queryset(customers)
        return self.paginated_response(
            request,
            customers,
            CustomerSerializer,
        )

    def post(self, request, slug):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace_id=self.get_workspace_id(slug))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailAPIEndpoint(BaseAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            deleted_at__isnull=True,
        )

    def get(self, request, slug, customer_id):
        customer = self.get_queryset().filter(pk=customer_id).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def patch(self, request, slug, customer_id):
        customer = self.get_queryset().filter(pk=customer_id).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, customer_id):
        customer = self.get_queryset().filter(pk=customer_id).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerContactsAPIEndpoint(BaseAPIView):
    serializer_class = CustomerContactSerializer

    def get_queryset(self):
        return CustomerContact.objects.filter(
            customer__workspace__slug=self.kwargs.get("slug"),
            customer_id=self.kwargs.get("customer_id"),
        )

    def get(self, request, slug, customer_id):
        customer = Customer.objects.filter(
            workspace__slug=slug,
            pk=customer_id,
            deleted_at__isnull=True,
        ).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        contacts = self.get_queryset()
        serializer = CustomerContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, slug, customer_id):
        customer = Customer.objects.filter(
            workspace__slug=slug,
            pk=customer_id,
            deleted_at__isnull=True,
        ).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerContactDetailAPIEndpoint(BaseAPIView):
    serializer_class = CustomerContactSerializer

    def get_queryset(self):
        return CustomerContact.objects.filter(
            customer__workspace__slug=self.kwargs.get("slug"),
            customer_id=self.kwargs.get("customer_id"),
        )

    def get(self, request, slug, customer_id, contact_id):
        contact = self.get_queryset().filter(pk=contact_id).first()
        if not contact:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerContactSerializer(contact)
        return Response(serializer.data)

    def patch(self, request, slug, customer_id, contact_id):
        contact = self.get_queryset().filter(pk=contact_id).first()
        if not contact:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, customer_id, contact_id):
        contact = self.get_queryset().filter(pk=contact_id).first()
        if not contact:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerItemsAPIEndpoint(BaseAPIView, BasePaginator):
    def get(self, request, slug, customer_id):
        customer = Customer.objects.filter(
            workspace__slug=slug,
            pk=customer_id,
            deleted_at__isnull=True,
        ).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        intake_issues = IntakeIssue.objects.filter(
            workspace__slug=slug,
            customer=customer,
        ).select_related("issue", "intake", "customer")

        issues = Issue.objects.filter(
            workspace__slug=slug,
            customer=customer,
        ).select_related("state", "project")

        from plane.api.serializers import IntakeIssueSerializer, IssueSerializer
        from plane.api.serializers.issue import IssueExpandSerializer

        intake_serializer = IntakeIssueSerializer(intake_issues, many=True)
        issue_serializer = IssueExpandSerializer(issues, many=True, context={"expand": []})

        return Response(
            {
                "intake_items": intake_serializer.data,
                "work_items": issue_serializer.data,
            }
        )


class CustomerCommentsAPIEndpoint(BaseAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return CustomerComment.objects.filter(
            customer__workspace__slug=self.kwargs.get("slug"),
            customer_id=self.kwargs.get("customer_id"),
        ).select_related("customer", "created_by")

    def get(self, request, slug, customer_id):
        customer = Customer.objects.filter(
            workspace__slug=slug,
            pk=customer_id,
            deleted_at__isnull=True,
        ).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        comments = self.get_queryset()
        serializer = CustomerCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, slug, customer_id):
        customer = Customer.objects.filter(
            workspace__slug=slug,
            pk=customer_id,
            deleted_at__isnull=True,
        ).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerCommentDetailAPIEndpoint(BaseAPIView):
    serializer_class = CustomerCommentSerializer

    def get_queryset(self):
        return CustomerComment.objects.filter(
            customer__workspace__slug=self.kwargs.get("slug"),
            customer_id=self.kwargs.get("customer_id"),
        )

    def get(self, request, slug, customer_id, comment_id):
        comment = self.get_queryset().filter(pk=comment_id).first()
        if not comment:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerCommentSerializer(comment)
        return Response(serializer.data)

    def patch(self, request, slug, customer_id, comment_id):
        comment = self.get_queryset().filter(pk=comment_id).first()
        if not comment:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, customer_id, comment_id):
        comment = self.get_queryset().filter(pk=comment_id).first()
        if not comment:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
