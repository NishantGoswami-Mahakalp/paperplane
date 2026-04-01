# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Test Settings"""

from .common import *  # noqa

DEBUG = True

# Contract tests should not require deployment-only host configuration.
WEB_URL = WEB_URL or "http://testserver"
APP_BASE_URL = APP_BASE_URL or "http://testserver"

# Send it in a dummy outbox
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Keep cache-backed features like throttling isolated per test process.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "plane-test-cache",
    }
}

INSTALLED_APPS.append(  # noqa
    "plane.tests"
)
