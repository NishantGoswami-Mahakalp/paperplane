# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports

# Django imports
from django.db import models

# Module imports
from plane.db.models.project import ProjectBaseModel


class ForgejoRepository(ProjectBaseModel):
    name = models.CharField(max_length=500)
    url = models.URLField(null=True)
    config = models.JSONField(default=dict)
    repository_id = models.BigIntegerField()
    owner = models.CharField(max_length=500)

    def __str__(self):
        """Return the repo name"""
        return f"{self.name}"

    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"
        db_table = "forgejo_repositories"
        ordering = ("-created_at",)


class ForgejoRepositorySync(ProjectBaseModel):
    repository = models.OneToOneField("db.ForgejoRepository", on_delete=models.CASCADE, related_name="syncs")
    credentials = models.JSONField(default=dict)
    # Bot user
    actor = models.ForeignKey("db.User", related_name="forgejo_user_syncs", on_delete=models.CASCADE)
    workspace_integration = models.ForeignKey(
        "db.WorkspaceIntegration", related_name="forgejo_syncs", on_delete=models.CASCADE
    )
    label = models.ForeignKey("db.Label", on_delete=models.SET_NULL, null=True, related_name="forgejo_repo_syncs")

    def __str__(self):
        """Return the repo sync"""
        return f"{self.repository.name} <{self.project.name}>"

    class Meta:
        unique_together = ["project", "repository"]
        verbose_name = "Forgejo Repository Sync"
        verbose_name_plural = "Forgejo Repository Syncs"
        db_table = "forgejo_repository_syncs"
        ordering = ("-created_at",)


class ForgejoIssueSync(ProjectBaseModel):
    repo_issue_id = models.BigIntegerField()
    forgejo_issue_id = models.BigIntegerField()
    issue_url = models.URLField(blank=False)
    issue = models.ForeignKey("db.Issue", related_name="forgejo_syncs", on_delete=models.CASCADE)
    repository_sync = models.ForeignKey(
        "db.ForgejoRepositorySync", related_name="issue_syncs", on_delete=models.CASCADE
    )

    def __str__(self):
        """Return the forgejo issue sync"""
        return f"{self.repository.name}-{self.project.name}-{self.issue.name}"

    class Meta:
        unique_together = ["repository_sync", "issue"]
        verbose_name = "Forgejo Issue Sync"
        verbose_name_plural = "Forgejo Issue Syncs"
        db_table = "forgejo_issue_syncs"
        ordering = ("-created_at",)


class ForgejoCommentSync(ProjectBaseModel):
    repo_comment_id = models.BigIntegerField()
    comment = models.ForeignKey("db.IssueComment", related_name="forgejo_comment_syncs", on_delete=models.CASCADE)
    issue_sync = models.ForeignKey("db.ForgejoIssueSync", related_name="comment_syncs", on_delete=models.CASCADE)

    def __str__(self):
        """Return the forgejo comment sync"""
        return f"{self.comment.id}"

    class Meta:
        unique_together = ["issue_sync", "comment"]
        verbose_name = "Forgejo Comment Sync"
        verbose_name_plural = "Forgejo Comment Syncs"
        db_table = "forgejo_comment_syncs"
        ordering = ("-created_at",)
