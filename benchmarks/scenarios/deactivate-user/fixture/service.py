from models import UserNotFound


class UserService:
    def __init__(self, repository):
        self.repository = repository

    def get_user(self, user_id: str):
        user = self.repository.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user
