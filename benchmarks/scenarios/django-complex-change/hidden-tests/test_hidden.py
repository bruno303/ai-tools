import inspect
import sys
import types
import unittest


# The benchmark runner intentionally does not install optional fixture
# dependencies. Supply only the small import-time compatibility surface needed
# by this HTTP-only test when asgiref is unavailable.
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

from django.conf import settings
from django.http import HttpRequest


if not settings.configured:
    settings.configure(DEFAULT_CHARSET="utf-8")


def request_with_accept(value):
    request = HttpRequest()
    if value is not None:
        request.META["HTTP_ACCEPT"] = value
    return request


class PreferredTypeBehaviorTests(unittest.TestCase):
    def test_quality_and_specificity_choose_the_best_offered_type(self):
        request = request_with_accept(
            "text/*;q=0.8, application/json;q=0.9, text/html;q=0.7"
        )
        self.assertEqual(
            request.get_preferred_type(["text/html", "application/json"]),
            "application/json",
        )

    def test_specificity_beats_a_less_specific_higher_header_entry(self):
        request = request_with_accept("text/*;q=0.8, text/html;q=0.8")
        self.assertEqual(request.get_preferred_type(["text/html"]), "text/html")

    def test_client_preference_beats_offer_order(self):
        request = request_with_accept("application/json, text/html;q=0.5")
        self.assertEqual(
            request.get_preferred_type(["text/html", "application/json"]),
            "application/json",
        )

    def test_parameters_are_part_of_media_type_matching(self):
        request = request_with_accept("text/vcard; version=3.0")
        self.assertEqual(
            request.get_preferred_type(
                ["text/vcard; version=4.0", "text/vcard; version=3.0"]
            ),
            "text/vcard; version=3.0",
        )

    def test_generator_is_consumed_as_an_ordered_iterable(self):
        offered = (item for item in ["text/plain", "application/json"])
        self.assertEqual(
            request_with_accept("application/json").get_preferred_type(offered),
            "application/json",
        )

    def test_wildcard_and_no_match(self):
        self.assertEqual(
            request_with_accept("text/*").get_preferred_type(
                ["application/json", "text/plain"]
            ),
            "text/plain",
        )
        self.assertIsNone(
            request_with_accept("application/json").get_preferred_type(
                ["text/html"]
            )
        )

    def test_rejected_types_and_empty_offers_return_none(self):
        request = request_with_accept("text/html;q=0, */*;q=0")
        self.assertIsNone(request.get_preferred_type(["text/html"]))
        self.assertIsNone(request.get_preferred_type([]))

    def test_empty_and_malformed_headers_have_defined_outcomes(self):
        self.assertIsNone(request_with_accept("").get_preferred_type(["text/plain"]))
        self.assertIsNone(
            request_with_accept("not-a-media-range").get_preferred_type(["text/plain"])
        )
        self.assertEqual(
            request_with_accept("not-a-media-range, text/plain").get_preferred_type(
                ["text/plain"]
            ),
            "text/plain",
        )

    def test_header_order_breaks_equal_quality_and_specificity_ties(self):
        request = request_with_accept("application/json, text/plain")
        self.assertEqual(
            request.get_preferred_type(["text/plain", "application/json"]),
            "application/json",
        )

    def test_offer_order_breaks_a_single_range_tie(self):
        request = request_with_accept("text/*")
        self.assertEqual(
            request.get_preferred_type(["text/plain", "text/html"]),
            "text/plain",
        )

    def test_q_zero_is_not_accepted(self):
        request = request_with_accept("text/plain;q=0, text/*;q=0")
        self.assertIsNone(request.get_preferred_type(["text/plain"]))

    def test_specific_q_zero_exclusion_overrides_positive_wildcard(self):
        request = request_with_accept("text/html;q=0, text/*;q=1")
        self.assertEqual(request.get_preferred_type(["text/html", "text/plain"]), "text/plain")

    def test_get_preferred_type_preserves_accepts_compatibility(self):
        request = request_with_accept("text/plain")
        self.assertTrue(request.accepts("text/plain"))
        self.assertFalse(request.accepts("image/png"))
        self.assertEqual(request.get_preferred_type(["text/plain"]), "text/plain")

    def test_missing_accept_header_defaults_to_any_type(self):
        self.assertEqual(
            request_with_accept(None).get_preferred_type(
                ["application/json", "text/plain"]
            ),
            "application/json",
        )


class PublicChangeEvidenceTests(unittest.TestCase):
    def test_public_regression_and_documentation_are_present(self):
        import subprocess

        public_test = "tests/requests_tests/test_accept_header.py"
        documentation = "docs/ref/request-response.txt"
        for path in (public_test, documentation):
            self.assertTrue(__import__("pathlib").Path(path).is_file(), path)
            diff = subprocess.run(["git", "diff", "--", path], capture_output=True, text=True, check=False)
            self.assertNotEqual(diff.stdout, "", f"{path} was not updated")
            self.assertIn("get_preferred_type", diff.stdout, path)


if __name__ == "__main__":
    unittest.main()
