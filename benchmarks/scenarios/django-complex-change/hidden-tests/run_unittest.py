"""Run unittest after installing this scenario's optional-dependency shims."""

import unittest

from dependency_stubs import configure_django_settings, install_dependency_stubs


if __name__ == "__main__":
    install_dependency_stubs()
    configure_django_settings()
    unittest.main(module=None)
