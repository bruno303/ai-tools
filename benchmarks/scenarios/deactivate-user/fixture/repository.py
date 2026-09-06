from models import User


class UserRepository:
    def __init__(self, users=None):
        self._users = {user.id: user for user in (users or [])}

    def get(self, user_id: str):
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user
