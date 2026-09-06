import unittest

from api import deactivate_user
from models import User, UserNotFound
from repository import UserRepository
from service import UserService


class HiddenDeactivateUserTests(unittest.TestCase):
    def test_service_deactivates_and_persists(self):
        repo = UserRepository([User("u1")])
        user = UserService(repo).deactivate_user("u1")
        self.assertFalse(user.active)
        self.assertFalse(repo.get("u1").active)

    def test_deactivation_is_idempotent(self):
        repo = UserRepository([User("u1", active=False)])
        user = UserService(repo).deactivate_user("u1")
        self.assertFalse(user.active)
        self.assertFalse(repo.get("u1").active)

    def test_missing_user_raises(self):
        with self.assertRaises(UserNotFound):
            UserService(UserRepository()).deactivate_user("missing")

    def test_api_returns_deactivated_state(self):
        repo = UserRepository([User("u1")])
        self.assertEqual({"id": "u1", "active": False}, deactivate_user(repo, "u1"))
        self.assertFalse(repo.get("u1").active)


if __name__ == "__main__":
    unittest.main()
