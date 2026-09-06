import unittest

from api import get_user
from models import User, UserNotFound
from repository import UserRepository
from service import UserService


class ExistingBehaviorTests(unittest.TestCase):
    def test_get_user(self):
        repo = UserRepository([User("u1")])
        self.assertEqual({"id": "u1", "active": True}, get_user(repo, "u1"))

    def test_missing_user_raises(self):
        with self.assertRaises(UserNotFound):
            UserService(UserRepository()).get_user("missing")


if __name__ == "__main__":
    unittest.main()
