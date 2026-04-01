import json

from django.core.management.base import BaseCommand, CommandError

from plane.api.agent_config import ensure_seva_project_configuration
from plane.db.models import Project


class Command(BaseCommand):
    help = "Create or normalize the Seva workflow, labels, issue types, and template for a Plane project."

    def add_arguments(self, parser):
        parser.add_argument("--workspace", required=True, help="Workspace slug")
        parser.add_argument("--project-id", required=True, help="Project UUID")

    def handle(self, *args, **options):
        workspace_slug = options["workspace"]
        project_id = options["project_id"]

        try:
            project = Project.objects.select_related("workspace", "workspace__owner").get(
                workspace__slug=workspace_slug,
                pk=project_id,
            )
        except Project.DoesNotExist as exc:
            raise CommandError("Project not found for the given workspace and project id") from exc

        actor = project.updated_by or project.created_by or project.workspace.owner
        configuration = ensure_seva_project_configuration(project, actor)

        self.stdout.write(
            json.dumps(
                {
                    "project_id": str(project.id),
                    "workspace": project.workspace.slug,
                    "configuration": configuration,
                },
                default=str,
                indent=2,
            )
        )
