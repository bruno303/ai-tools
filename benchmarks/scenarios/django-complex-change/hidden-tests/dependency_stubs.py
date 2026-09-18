"""Small import-time shims for the HTTP-only Django verification."""

import inspect
import sys
import types


def install_dependency_stubs():
    """Provide only the optional imports needed by this scenario when absent."""
    try:
        import asgiref.sync  # noqa: F401
    except ModuleNotFoundError:
        asgiref = types.ModuleType("asgiref")
        sync = types.ModuleType("asgiref.sync")
        sync.iscoroutinefunction = inspect.iscoroutinefunction
        sync.markcoroutinefunction = lambda function: function
        sync.sync_to_async = lambda function=None, **kwargs: function
        sync.async_to_sync = lambda function=None, **kwargs: function
        asgiref.sync = sync
        local = types.ModuleType("asgiref.local")
        local.Local = type("Local", (), {"__init__": lambda self, *args, **kwargs: None})
        asgiref.local = local
        sys.modules["asgiref"] = asgiref
        sys.modules["asgiref.sync"] = sync
        sys.modules["asgiref.local"] = local

    try:
        import sqlparse  # noqa: F401
    except ModuleNotFoundError:
        sys.modules["sqlparse"] = types.ModuleType("sqlparse")


def configure_django_settings():
    """Configure the minimal Django settings needed by HTTP-only tests."""
    try:
        from django.conf import settings
    except ModuleNotFoundError as error:
        if error.name == "django":
            return
        raise

    if not settings.configured:
        settings.configure(DEFAULT_CHARSET="utf-8")
