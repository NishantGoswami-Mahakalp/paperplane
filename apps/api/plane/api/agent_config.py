from collections import defaultdict

from django.db import transaction

from plane.db.models import (
    IssueTemplate,
    IssueType,
    Label,
    ProjectIssueType,
    State,
    StateAgentType,
    StateGroup,
)

SEVA_TEMPLATE_NAME = "Seva Work Item"

SEVA_DESCRIPTION_TEMPLATE = {
    "sections": [
        "Why",
        "What",
        "Acceptance Criteria",
        "Dependencies",
        "Notes / Handoff",
    ],
    "markdown": (
        "## Why\nWhy this work matters.\n\n"
        "## What\nWhat must be changed.\n\n"
        "## Acceptance Criteria\n- condition 1\n- condition 2\n\n"
        "## Dependencies\n- blocking issue or external dependency\n\n"
        "## Notes / Handoff\nRelevant context, links, or constraints.\n"
    ),
    "html": (
        "<h2>Why</h2><p>Why this work matters.</p>"
        "<h2>What</h2><p>What must be changed.</p>"
        "<h2>Acceptance Criteria</h2><ul><li>condition 1</li><li>condition 2</li></ul>"
        "<h2>Dependencies</h2><ul><li>blocking issue or external dependency</li></ul>"
        "<h2>Notes / Handoff</h2><p>Relevant context, links, or constraints.</p>"
    ),
}

SEVA_OPERATING_RULES = {
    "allowed_project_strategy": "dedicated_project",
    "auto_assign_issues": False,
    "close_parent_issues": False,
    "metadata_source": {
        "severity": "labels",
        "component": "labels",
        "environment": "labels",
    },
    "event_intake": {
        "mode": "polling",
        "poll_interval_seconds": 60,
        "cursor_strategy": "updated_at_then_id",
    },
}

SEVA_STATE_SPECS = [
    {
        "agent_state": StateAgentType.BACKLOG.value,
        "name": "Backlog",
        "group": StateGroup.BACKLOG.value,
        "color": "#60646C",
        "sequence": 15000,
        "default": True,
        "description": "Deferred work that is not actionable yet.",
    },
    {
        "agent_state": StateAgentType.READY.value,
        "name": "Ready",
        "group": StateGroup.UNSTARTED.value,
        "color": "#3E63DD",
        "sequence": 25000,
        "default": False,
        "description": "Unblocked work that Seva may pick up now.",
    },
    {
        "agent_state": StateAgentType.IN_PROGRESS.value,
        "name": "In Progress",
        "group": StateGroup.STARTED.value,
        "color": "#F59E0B",
        "sequence": 35000,
        "default": False,
        "description": "Actively owned work in flight.",
    },
    {
        "agent_state": StateAgentType.BLOCKED.value,
        "name": "Blocked",
        "group": StateGroup.STARTED.value,
        "color": "#E5484D",
        "sequence": 45000,
        "default": False,
        "description": "Work that cannot progress because of an external dependency.",
    },
    {
        "agent_state": StateAgentType.IN_REVIEW.value,
        "name": "In Review",
        "group": StateGroup.STARTED.value,
        "color": "#8E4EC6",
        "sequence": 55000,
        "default": False,
        "description": "Implementation is complete and awaiting review or verification.",
    },
    {
        "agent_state": StateAgentType.DONE.value,
        "name": "Done",
        "group": StateGroup.COMPLETED.value,
        "color": "#46A758",
        "sequence": 65000,
        "default": False,
        "description": "Acceptance criteria are satisfied and the work is complete.",
    },
    {
        "agent_state": StateAgentType.CANCELLED.value,
        "name": "Cancelled",
        "group": StateGroup.CANCELLED.value,
        "color": "#9AA4BC",
        "sequence": 75000,
        "default": False,
        "description": "The work was intentionally abandoned.",
    },
]

SEVA_ISSUE_TYPE_SPECS = [
    {"name": "task", "description": "Standard implementation work.", "is_default": True, "level": 0},
    {"name": "bug", "description": "A defect that must be fixed.", "is_default": False, "level": 1},
    {"name": "feature", "description": "New product or platform capability.", "is_default": False, "level": 2},
    {"name": "ops", "description": "Operational, infrastructure, or runbook work.", "is_default": False, "level": 3},
    {
        "name": "follow_up",
        "description": "Discovered work linked back to the originating issue.",
        "is_default": False,
        "level": 4,
    },
]

SEVA_LABEL_TAXONOMY = {
    "severity": ["critical", "high", "medium", "low"],
    "component": ["api", "web", "auth", "billing", "infra", "docs"],
    "environment": ["prod", "staging", "sandbox"],
}


def _serialize_issue_type(issue_type):
    return {
        "id": issue_type.id,
        "name": issue_type.name,
        "description": issue_type.description,
        "is_default": issue_type.is_default,
        "level": issue_type.level,
    }


def _serialize_label(label):
    return {
        "id": label.id,
        "name": label.name,
        "description": label.description,
        "color": label.color,
        "parent": label.parent_id,
    }


def _serialize_state(state):
    return {
        "id": state.id,
        "name": state.name,
        "group": state.group,
        "agent_state": state.agent_state,
        "color": state.color,
        "default": state.default,
        "description": state.description,
    }


def _serialize_issue_template(issue_template):
    if issue_template is None:
        return None

    return {
        "id": issue_template.id,
        "name": issue_template.name,
        "description": issue_template.description,
        "description_html": issue_template.description_html,
        "state_id": issue_template.state_id,
        "type_id": issue_template.type_id,
    }


def get_seva_issue_types(project):
    return list(
        IssueType.objects.filter(project_issue_types__project=project, deleted_at__isnull=True)
        .distinct()
        .order_by("project_issue_types__level", "name")
    )


def get_seva_configuration(project):
    states = list(State.all_state_objects.filter(project=project, deleted_at__isnull=True).order_by("sequence"))
    states_by_agent_state = {state.agent_state: state for state in states if state.agent_state}

    issue_types = get_seva_issue_types(project)
    issue_types_by_name = {issue_type.name: issue_type for issue_type in issue_types}

    labels = list(
        Label.objects.filter(project=project, deleted_at__isnull=True).select_related("parent").order_by("name")
    )
    root_labels_by_name = {}
    labels_by_parent_id = defaultdict(list)
    for label in labels:
        if label.parent is None:
            root_labels_by_name[label.name] = label
        else:
            labels_by_parent_id[label.parent_id].append(label)

    issue_template = IssueTemplate.objects.filter(project=project, name=SEVA_TEMPLATE_NAME).first()

    missing_states = [
        state_spec["agent_state"]
        for state_spec in SEVA_STATE_SPECS
        if state_spec["agent_state"] not in states_by_agent_state
    ]
    missing_issue_types = [
        issue_type_spec["name"]
        for issue_type_spec in SEVA_ISSUE_TYPE_SPECS
        if issue_type_spec["name"] not in issue_types_by_name
    ]
    missing_labels = {}
    for category, label_names in SEVA_LABEL_TAXONOMY.items():
        root_label = root_labels_by_name.get(category)
        category_labels = labels_by_parent_id.get(root_label.id, []) if root_label else []
        category_label_names = {label.name for label in category_labels}
        missing_category_labels = [label_name for label_name in label_names if label_name not in category_label_names]
        if missing_category_labels:
            missing_labels[category] = missing_category_labels

    missing_labels = {category: label_names for category, label_names in missing_labels.items() if label_names}

    return {
        "is_ready": not missing_states
        and not missing_issue_types
        and not missing_labels
        and issue_template is not None,
        "operating_rules": SEVA_OPERATING_RULES,
        "states": {
            state_spec["agent_state"]: _serialize_state(states_by_agent_state[state_spec["agent_state"]])
            for state_spec in SEVA_STATE_SPECS
            if state_spec["agent_state"] in states_by_agent_state
        },
        "issue_types": [_serialize_issue_type(issue_type) for issue_type in issue_types],
        "label_taxonomy": {
            category: [
                _serialize_label(label) for label in labels_by_parent_id.get(root_labels_by_name[category].id, [])
            ]
            for category in SEVA_LABEL_TAXONOMY
            if category in root_labels_by_name
        },
        "issue_template": _serialize_issue_template(issue_template),
        "missing": {
            "states": missing_states,
            "issue_types": missing_issue_types,
            "labels": missing_labels,
            "issue_template": issue_template is None,
        },
    }


@transaction.atomic
def ensure_seva_project_configuration(project, actor):
    states_by_agent_state = {
        state.agent_state: state
        for state in State.all_state_objects.filter(project=project, deleted_at__isnull=True)
        if state.agent_state
    }
    states_by_name = {
        state.name.lower(): state for state in State.all_state_objects.filter(project=project, deleted_at__isnull=True)
    }

    configured_states = {}
    for state_spec in SEVA_STATE_SPECS:
        state = states_by_agent_state.get(state_spec["agent_state"]) or states_by_name.get(state_spec["name"].lower())
        if state is None:
            state = State.all_state_objects.create(
                project=project,
                workspace=project.workspace,
                name=state_spec["name"],
                description=state_spec["description"],
                color=state_spec["color"],
                sequence=state_spec["sequence"],
                group=state_spec["group"],
                agent_state=state_spec["agent_state"],
                default=state_spec["default"],
                created_by=actor,
                updated_by=actor,
            )
        else:
            state.name = state_spec["name"]
            state.description = state_spec["description"]
            state.color = state_spec["color"]
            state.sequence = state_spec["sequence"]
            state.group = state_spec["group"]
            state.agent_state = state_spec["agent_state"]
            state.default = state_spec["default"]
            state.updated_by = actor
            state.save(
                update_fields=[
                    "name",
                    "description",
                    "color",
                    "sequence",
                    "group",
                    "agent_state",
                    "default",
                    "updated_by",
                    "slug",
                ]
            )
        configured_states[state_spec["agent_state"]] = state

    State.all_state_objects.filter(project=project, deleted_at__isnull=True).exclude(
        pk=configured_states[StateAgentType.BACKLOG.value].pk
    ).filter(default=True).update(default=False, updated_by_id=actor.id)

    issue_types_by_name = {
        issue_type.name: issue_type
        for issue_type in IssueType.objects.filter(workspace=project.workspace, deleted_at__isnull=True)
    }
    configured_issue_types = {}
    for issue_type_spec in SEVA_ISSUE_TYPE_SPECS:
        issue_type = issue_types_by_name.get(issue_type_spec["name"])
        if issue_type is None:
            issue_type = IssueType.objects.create(
                workspace=project.workspace,
                name=issue_type_spec["name"],
                description=issue_type_spec["description"],
                is_default=issue_type_spec["is_default"],
                is_active=True,
                level=issue_type_spec["level"],
                created_by=actor,
                updated_by=actor,
            )
        else:
            issue_type.description = issue_type_spec["description"]
            issue_type.is_default = issue_type_spec["is_default"]
            issue_type.is_active = True
            issue_type.level = issue_type_spec["level"]
            issue_type.updated_by = actor
            issue_type.save(update_fields=["description", "is_default", "is_active", "level", "updated_by"])

        ProjectIssueType.objects.update_or_create(
            project=project,
            issue_type=issue_type,
            defaults={
                "workspace": project.workspace,
                "level": issue_type_spec["level"],
                "is_default": issue_type_spec["is_default"],
                "created_by": actor,
                "updated_by": actor,
            },
        )
        configured_issue_types[issue_type_spec["name"]] = issue_type

    parent_labels = {}
    for category in SEVA_LABEL_TAXONOMY:
        parent_label, _ = Label.objects.update_or_create(
            project=project,
            name=category,
            defaults={
                "workspace": project.workspace,
                "description": f"Seva {category} taxonomy root.",
                "color": "#60646C",
                "parent": None,
                "created_by": actor,
                "updated_by": actor,
            },
        )
        parent_labels[category] = parent_label

    for category, label_names in SEVA_LABEL_TAXONOMY.items():
        for label_name in label_names:
            Label.objects.update_or_create(
                project=project,
                name=label_name,
                defaults={
                    "workspace": project.workspace,
                    "description": f"Seva {category} label.",
                    "color": "#3E63DD",
                    "parent": parent_labels[category],
                    "created_by": actor,
                    "updated_by": actor,
                },
            )

    IssueTemplate.objects.update_or_create(
        project=project,
        name=SEVA_TEMPLATE_NAME,
        defaults={
            "workspace": project.workspace,
            "description": "Canonical Seva work item template.",
            "description_html": SEVA_DESCRIPTION_TEMPLATE["html"],
            "state": configured_states[StateAgentType.READY.value],
            "type": configured_issue_types["task"],
            "created_by": actor,
            "updated_by": actor,
        },
    )

    return get_seva_configuration(project)
