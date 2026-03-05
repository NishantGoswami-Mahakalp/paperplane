# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db import transaction
from django.utils import timezone

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ROLE, allow_permission
from plane.app.serializers.worklog import WorkLogCreateSerializer, WorkLogSerializer
from plane.db.models import Issue, TimerSession, WorkLog

from .. import BaseAPIView, BaseViewSet


class WorkLogViewSet(BaseViewSet):
    model = WorkLog
    serializer_class = WorkLogSerializer

    def get_queryset(self):
        return WorkLog.objects.filter(
            item_id=self.kwargs.get("item_id"),
            project_id=self.kwargs.get("project_id"),
            workspace__slug=self.kwargs.get("slug"),
        )

    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def create(self, request, slug, project_id, item_id):
        serializer = WorkLogCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                worklog = serializer.save(
                    item_id=item_id,
                    project_id=project_id,
                    user=request.user,
                )
            return Response(WorkLogSerializer(worklog).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkLogListEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def get(self, request, slug, project_id, item_id):
        worklogs = WorkLog.objects.filter(
            item_id=item_id,
            project_id=project_id,
            workspace__slug=slug,
        ).select_related("user")

        serializer = WorkLogSerializer(worklogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimerStartEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, item_id):
        try:
            with transaction.atomic():
                running_timer = (
                    TimerSession.objects.filter(
                        workspace__slug=slug,
                        user=request.user,
                        is_running=True,
                    )
                    .select_for_update()
                    .first()
                )

                if running_timer:
                    return Response(
                        {
                            "error": "A timer is already running for this user in this workspace",
                            "running_timer": {
                                "id": str(running_timer.id),
                                "item_id": str(running_timer.item_id),
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                timer = TimerSession.objects.create(
                    item_id=item_id,
                    project_id=project_id,
                    user=request.user,
                    started_at=request.data.get("started_at") or timezone.now(),
                    is_running=True,
                )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from plane.app.serializers.timer_session import TimerSessionSerializer

        return Response(TimerSessionSerializer(timer).data, status=status.HTTP_201_CREATED)


class TimerStopEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER])
    def post(self, request, slug, project_id, item_id):
        with transaction.atomic():
            timer = TimerSession.objects.filter(
                item_id=item_id,
                project_id=project_id,
                workspace__slug=slug,
                user=request.user,
                is_running=True,
            ).first()

            if not timer:
                return Response(
                    {"error": "No running timer found for this item"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            timer.ended_at = request.data.get("ended_at") or timezone.now()
            timer.is_running = False
            timer.save()

            duration_minutes = int((timer.ended_at - timer.started_at).total_seconds() / 60)

            worklog = WorkLog.objects.create(
                item_id=item_id,
                project_id=project_id,
                user=request.user,
                started_at=timer.started_at,
                ended_at=timer.ended_at,
                duration_minutes=duration_minutes,
                description=request.data.get("description", ""),
            )

        from plane.app.serializers.timer_session import TimerSessionSerializer
        from plane.app.serializers.worklog import WorkLogSerializer

        return Response(
            {
                "timer": TimerSessionSerializer(timer).data,
                "worklog": WorkLogSerializer(worklog).data,
            },
            status=status.HTTP_200_OK,
        )


class TimerDetailEndpoint(BaseAPIView):
    @allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])
    def get(self, request, slug, project_id, item_id):
        timer = TimerSession.objects.filter(
            item_id=item_id,
            project_id=project_id,
            workspace__slug=slug,
            is_running=True,
        ).first()

        if not timer:
            return Response(
                {"error": "No running timer found for this item"},
                status=status.HTTP_404_NOT_FOUND,
            )

        from plane.app.serializers.timer_session import TimerSessionSerializer

        return Response(TimerSessionSerializer(timer).data, status=status.HTTP_200_OK)
