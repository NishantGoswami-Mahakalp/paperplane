# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db import IntegrityError

# Third party imports
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

# Module imports
from plane.app.views.base import BaseViewSet
from plane.db.models import (
    WorkItemType,
    ProjectWorkItemType,
    FieldDefinition,
    WorkItemTypeField,
    get_default_work_item_fields,
    Workspace,
)
from plane.api.serializers.work_item_type import (
    WorkItemTypeSerializer,
    WorkItemTypeLiteSerializer,
    WorkItemTypeCreateSerializer,
    ProjectWorkItemTypeSerializer,
    ProjectWorkItemTypeCreateSerializer,
    FieldDefinitionSerializer,
    FieldDefinitionLiteSerializer,
    WorkItemTypeFieldSerializer,
    WorkItemTypeFieldCreateSerializer,
)
from plane.utils.exception_logger import log_exception


class WorkItemTypeViewSet(BaseViewSet):
    model = WorkItemType
    serializer_class = WorkItemTypeSerializer
    filterset_fields = ["name", "work_item_type", "is_default", "is_active", "is_epic"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        workspace = Workspace.objects.get(slug=slug)
        return WorkItemType.objects.filter(workspace=workspace)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return WorkItemTypeSerializer
        return WorkItemTypeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slug = self.kwargs.get("slug")
        workspace = Workspace.objects.get(slug=slug)
        name = serializer.validated_data.get("name")
        work_item_type_value = serializer.validated_data.get("work_item_type", "task")
        description = serializer.validated_data.get("description", "")
        logo_props = serializer.validated_data.get("logo_props", {})
        is_default = serializer.validated_data.get("is_default", False)
        is_epic = serializer.validated_data.get("is_epic", False)
        is_active = serializer.validated_data.get("is_active", True)

        try:
            work_item_type_obj = WorkItemType.objects.create(
                workspace=workspace,
                name=name,
                work_item_type=work_item_type_value,
                description=description,
                logo_props=logo_props,
                is_default=is_default,
                is_epic=is_epic,
                is_active=is_active,
                created_by=request.user,
            )

            default_fields = serializer.validated_data.get("default_fields")
            if default_fields is None:
                default_fields = get_default_work_item_fields(work_item_type_value)

            for field_data in default_fields:
                field_name = field_data.get("field_name")
                field_type = field_data.get("field_type", "text")
                is_required = field_data.get("is_required", False)
                position = field_data.get("position", 0)
                validations = field_data.get("validations", {})

                field_def, _ = FieldDefinition.objects.get_or_create(
                    workspace=workspace,
                    name=field_name,
                    defaults={
                        "field_type": field_type,
                        "description": "",
                        "validation_rules": validations,
                        "created_by": request.user,
                    },
                )

                WorkItemTypeField.objects.create(
                    work_item_type=work_item_type_obj,
                    field_definition=field_def,
                    is_required=is_required,
                    position=position,
                    validations=validations,
                    created_by=request.user,
                )

            serializer = WorkItemTypeSerializer(work_item_type_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "Work item type with this name already exists in the workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_exception(e)
            return Response(
                {"error": "Failed to create work item type"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FieldDefinitionViewSet(BaseViewSet):
    model = FieldDefinition
    serializer_class = FieldDefinitionSerializer
    filterset_fields = ["name", "field_type", "is_required"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        workspace = Workspace.objects.get(slug=slug)
        return FieldDefinition.objects.filter(workspace=workspace)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return FieldDefinitionSerializer
        return FieldDefinitionSerializer


class ProjectWorkItemTypeViewSet(BaseViewSet):
    model = ProjectWorkItemType
    serializer_class = ProjectWorkItemTypeSerializer
    filterset_fields = ["is_default"]
    search_fields = []

    def get_queryset(self):
        project_id = self.kwargs.get("project_id", None)
        if project_id:
            return ProjectWorkItemType.objects.filter(project_id=project_id)
        return ProjectWorkItemType.objects.none()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProjectWorkItemTypeSerializer
        return ProjectWorkItemTypeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = kwargs.get("project_id")
        work_item_type_id = serializer.validated_data.get("work_item_type_id")
        position = serializer.validated_data.get("position", 0)
        is_default = serializer.validated_data.get("is_default", False)

        try:
            project_work_item_type = ProjectWorkItemType.objects.create(
                project_id=project_id,
                work_item_type_id=work_item_type_id,
                position=position,
                is_default=is_default,
                created_by=request.user,
            )

            serializer = ProjectWorkItemTypeSerializer(project_work_item_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "This work item type is already associated with the project"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_exception(e)
            return Response(
                {"error": "Failed to add work item type to project"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WorkItemTypeFieldViewSet(BaseViewSet):
    model = WorkItemTypeField
    serializer_class = WorkItemTypeFieldSerializer
    filterset_fields = ["is_required"]
    search_fields = []

    def get_queryset(self):
        work_item_type_id = self.kwargs.get("work_item_type_id", None)
        if work_item_type_id:
            return WorkItemTypeField.objects.filter(work_item_type_id=work_item_type_id)
        return WorkItemTypeField.objects.none()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return WorkItemTypeFieldSerializer
        return WorkItemTypeFieldCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_item_type_id = kwargs.get("work_item_type_id")
        field_definition_id = serializer.validated_data.get("field_definition_id")
        is_required = serializer.validated_data.get("is_required", False)
        position = serializer.validated_data.get("position", 0)
        validations = serializer.validated_data.get("validations", {})

        try:
            work_item_type_field = WorkItemTypeField.objects.create(
                work_item_type_id=work_item_type_id,
                field_definition_id=field_definition_id,
                is_required=is_required,
                position=position,
                validations=validations,
                created_by=request.user,
            )

            serializer = WorkItemTypeFieldSerializer(work_item_type_field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "This field is already associated with the work item type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_exception(e)
            return Response(
                {"error": "Failed to add field to work item type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
