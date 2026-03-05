# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db.models import Case, When, IntegerField, Value, F


def filter_by_health_score(queryset, health_score):
    """
    Filter customers by health score.
    Health score is calculated as: (closed_issues / total_issues) * 100
    """
    health_score = int(health_score)

    queryset = queryset.annotate(
        health_score_calc=Case(
            When(
                issue_count__gt=0,
                then=100 - (100 * F("open_issue_count") / F("issue_count")),
            ),
            default=Value(100),
            output_field=IntegerField(),
        )
    )

    if health_score == 0:
        queryset = queryset.filter(health_score_calc__lte=25)
    elif health_score == 1:
        queryset = queryset.filter(health_score_calc__gt=25, health_score_calc__lte=50)
    elif health_score == 2:
        queryset = queryset.filter(health_score_calc__gt=50, health_score_calc__lte=75)
    elif health_score == 3:
        queryset = queryset.filter(health_score_calc__gt=75)

    return queryset
