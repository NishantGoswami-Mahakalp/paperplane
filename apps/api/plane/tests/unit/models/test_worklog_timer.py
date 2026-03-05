# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
import threading
import time
from uuid import uuid4

from django.utils import timezone
from django.db import connection

from plane.db.models import Issue, Project, TimerSession, WorkLog


@pytest.mark.unit
class TestWorkLogModel:
    """Test the WorkLog model"""

    @pytest.mark.django_db
    def test_worklog_creation(self, create_user, workspace, project):
        """Test creating a worklog"""
        issue = Issue.objects.create(
            name="Test Issue",
            project=project,
            workspace=workspace,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=30)

        worklog = WorkLog.objects.create(
            item=issue,
            user=create_user,
            duration_minutes=30,
            started_at=start_time,
            ended_at=end_time,
            description="Test work",
            project=project,
            workspace=workspace,
        )

        assert worklog.id is not None
        assert worklog.item == issue
        assert worklog.user == create_user
        assert worklog.duration_minutes == 30
        assert worklog.description == "Test work"

    @pytest.mark.django_db
    def test_worklog_with_project_workspace(self, create_user, workspace, project):
        """Test that worklog gets workspace from project"""
        issue = Issue.objects.create(
            name="Test Issue",
            project=project,
            workspace=workspace,
        )

        start_time = timezone.now()
        worklog = WorkLog.objects.create(
            item=issue,
            user=create_user,
            duration_minutes=15,
            started_at=start_time,
            project=project,
            workspace=workspace,
        )

        assert worklog.workspace == workspace
        assert worklog.project == project


@pytest.mark.unit
class TestTimerSessionModel:
    """Test the TimerSession model"""

    @pytest.mark.django_db
    def test_timer_session_creation(self, create_user, workspace, project):
        """Test creating a timer session"""
        issue = Issue.objects.create(
            name="Test Issue",
            project=project,
            workspace=workspace,
        )

        start_time = timezone.now()

        timer = TimerSession.objects.create(
            item=issue,
            user=create_user,
            started_at=start_time,
            is_running=True,
            project=project,
            workspace=workspace,
        )

        assert timer.id is not None
        assert timer.item == issue
        assert timer.user == create_user
        assert timer.is_running is True
        assert timer.ended_at is None

    @pytest.mark.django_db
    def test_unique_running_timer_constraint(self, create_user, workspace, project):
        """Test that only one running timer per user per workspace is allowed"""
        issue1 = Issue.objects.create(
            name="Test Issue 1",
            project=project,
            workspace=workspace,
        )
        issue2 = Issue.objects.create(
            name="Test Issue 2",
            project=project,
            workspace=workspace,
        )

        start_time = timezone.now()

        TimerSession.objects.create(
            item=issue1,
            user=create_user,
            started_at=start_time,
            is_running=True,
            project=project,
            workspace=workspace,
        )

        with pytest.raises(Exception):
            TimerSession.objects.create(
                item=issue2,
                user=create_user,
                started_at=start_time,
                is_running=True,
                project=project,
                workspace=workspace,
            )

    @pytest.mark.django_db
    def test_multiple_stopped_timers_allowed(self, create_user, workspace, project):
        """Test that multiple stopped timers are allowed"""
        issue1 = Issue.objects.create(
            name="Test Issue 1",
            project=project,
            workspace=workspace,
        )
        issue2 = Issue.objects.create(
            name="Test Issue 2",
            project=project,
            workspace=workspace,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=30)

        TimerSession.objects.create(
            item=issue1,
            user=create_user,
            started_at=start_time,
            ended_at=end_time,
            is_running=False,
            project=project,
            workspace=workspace,
        )

        TimerSession.objects.create(
            item=issue2,
            user=create_user,
            started_at=start_time,
            ended_at=end_time,
            is_running=False,
            project=project,
            workspace=workspace,
        )

        timers = TimerSession.objects.filter(user=create_user, is_running=False)
        assert timers.count() == 2


@pytest.mark.unit
class TestConcurrentTimerRaceConditions:
    """Test concurrent timer operations for race conditions"""

    @pytest.mark.django_db
    def test_concurrent_timer_start_race_condition(self, create_user, workspace, project):
        """Test race condition when starting timers concurrently"""
        issue = Issue.objects.create(
            name="Test Issue",
            project=project,
            workspace=workspace,
        )

        errors = []
        created_count = [0]
        lock = threading.Lock()

        def create_timer():
            try:
                start_time = timezone.now()
                timer = TimerSession.objects.create(
                    item=issue,
                    user=create_user,
                    started_at=start_time,
                    is_running=True,
                    project=project,
                    workspace=workspace,
                )
                with lock:
                    created_count[0] += 1
            except Exception as e:
                with lock:
                    errors.append(str(e))

        threads = []
        for _ in range(5):
            t = threading.Thread(target=create_timer)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        running_timers = TimerSession.objects.filter(user=create_user, is_running=True)
        assert running_timers.count() == 1, f"Expected 1 running timer, got {running_timers.count()}. Errors: {errors}"

    @pytest.mark.django_db(transaction=True)
    def test_concurrent_timer_start_with_transaction(self, create_user, workspace, project):
        """Test race condition with transaction.atomic"""
        from django.db import transaction

        issue = Issue.objects.create(
            name="Test Issue",
            project=project,
            workspace=workspace,
        )

        errors = []
        success_count = [0]
        lock = threading.Lock()

        def create_timer_with_transaction():
            try:
                with transaction.atomic():
                    existing = TimerSession.objects.filter(
                        workspace=workspace,
                        user=create_user,
                        is_running=True,
                    ).first()

                    if existing:
                        with lock:
                            errors.append("Timer already running")
                        return

                    start_time = timezone.now()
                    TimerSession.objects.create(
                        item=issue,
                        user=create_user,
                        started_at=start_time,
                        is_running=True,
                        project=project,
                        workspace=workspace,
                    )
                    with lock:
                        success_count[0] += 1
            except Exception as e:
                with lock:
                    errors.append(str(e))

        threads = []
        for _ in range(5):
            t = threading.Thread(target=create_timer_with_transaction)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        running_timers = TimerSession.objects.filter(user=create_user, is_running=True)
        assert running_timers.count() == 1


@pytest.fixture
def project(db, create_user, workspace):
    """Create a project for testing"""
    project = Project.objects.create(
        name="Test Project",
        identifier="TP",
        workspace=workspace,
    )
    return project
