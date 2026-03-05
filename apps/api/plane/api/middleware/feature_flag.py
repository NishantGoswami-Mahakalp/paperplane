# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from functools import wraps
from typing import Callable, Dict, List, Optional

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from plane.db.models import FeatureFlag, FeatureFlagValue


class FeatureFlagMiddleware:
    """
    Middleware to check feature flags for API endpoints.
    Can be used as a decorator to protect views based on feature flags.
    """

    CACHE: Dict[str, bool] = {}
    CACHE_TTL = 300  # 5 minutes

    @classmethod
    def get_feature_flag_value(
        cls,
        flag_key: str,
        level: str,
        entity_id: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Get the value of a feature flag for a given entity.
        
        Priority:
        1. Check FeatureFlagValue table
        2. Check FeatureFlag default_enabled if no value exists
        3. Return False if flag doesn't exist
        """
        cache_key = f"{flag_key}:{level}:{entity_id}:{workspace_id}:{project_id}:{user_id}"
        
        # Check cache first
        if cache_key in cls.CACHE:
            return cls.CACHE[cache_key]

        try:
            flag = FeatureFlag.objects.get(key=flag_key)
        except FeatureFlag.DoesNotExist:
            cls.CACHE[cache_key] = False
            return False

        # Check if there's an explicit value
        query = Q(feature_flag=flag, level=level, entity_id=entity_id)
        
        if workspace_id:
            query &= Q(workspace_id=workspace_id)
        if project_id:
            query &= Q(project_id=project_id)
        if user_id:
            query &= Q(user_id=user_id)

        flag_value = FeatureFlagValue.objects.filter(query).first()

        if flag_value:
            result = flag_value.enabled
        else:
            result = flag.default_enabled

        cls.CACHE[cache_key] = result
        return result

    @classmethod
    def clear_cache(cls):
        """Clear the feature flag cache"""
        cls.CACHE.clear()

    @classmethod
    def is_feature_enabled(
        cls,
        flag_key: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Check if a feature flag is enabled.
        
        Priority order:
        1. User level
        2. Project level
        3. Workspace level
        """
        if user_id:
            user_enabled = cls.get_feature_flag_value(
                flag_key, "USER", user_id, user_id=user_id
            )
            if user_enabled:
                return True

        if project_id:
            project_enabled = cls.get_feature_flag_value(
                flag_key, "PROJECT", project_id, workspace_id=workspace_id, project_id=project_id
            )
            if project_enabled:
                return True

        if workspace_id:
            workspace_enabled = cls.get_feature_flag_value(
                flag_key, "WORKSPACE", workspace_id, workspace_id=workspace_id
            )
            if workspace_enabled:
                return True

        # Check for default value
        return cls.get_feature_flag_value(flag_key, "WORKSPACE", "default")


def feature_flag_required(
    flag_key: str,
    level: str = "WORKSPACE",
    entity_param: str = "workspace_slug",
):
    """
    Decorator to require a feature flag for a view.
    
    Args:
        flag_key: The feature flag key to check
        level: The level of the flag (WORKSPACE, PROJECT, USER)
        entity_param: The URL parameter to use for entity ID (e.g., 'workspace_slug', 'project_id')
    
    Usage:
        @feature_flag_required('ai_assistant', 'WORKSPACE', 'workspace_slug')
        def my_view(request, workspace_slug):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            entity_id = kwargs.get(entity_param)
            
            if not entity_id:
                return Response(
                    {"error": f"Missing required parameter: {entity_param}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            workspace_id = kwargs.get("workspace_slug")
            project_id = kwargs.get("project_id")
            user_id = str(request.user.id) if request.user.is_authenticated else None

            is_enabled = FeatureFlagMiddleware.is_feature_enabled(
                flag_key,
                workspace_id=workspace_id,
                project_id=project_id,
                user_id=user_id,
            )

            if not is_enabled:
                return Response(
                    {"error": f"Feature '{flag_key}' is not enabled"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def check_feature_flags(
    flags: List[str],
    level: str = "WORKSPACE",
    entity_param: str = "workspace_slug",
):
    """
    Decorator to require multiple feature flags for a view.
    
    Args:
        flags: List of feature flag keys to check
        level: The level of the flags (WORKSPACE, PROJECT, USER)
        entity_param: The URL parameter to use for entity ID
    
    Usage:
        @check_feature_flags(['ai_assistant', 'analytics'], 'WORKSPACE', 'workspace_slug')
        def my_view(request, workspace_slug):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            entity_id = kwargs.get(entity_param)
            
            if not entity_id:
                return Response(
                    {"error": f"Missing required parameter: {entity_param}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            workspace_id = kwargs.get("workspace_slug")
            project_id = kwargs.get("project_id")
            user_id = str(request.user.id) if request.user.is_authenticated else None

            disabled_flags = []
            for flag_key in flags:
                is_enabled = FeatureFlagMiddleware.is_feature_enabled(
                    flag_key,
                    workspace_id=workspace_id,
                    project_id=project_id,
                    user_id=user_id,
                )
                if not is_enabled:
                    disabled_flags.append(flag_key)

            if disabled_flags:
                return Response(
                    {"error": f"Features are not enabled: {', '.join(disabled_flags)"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
