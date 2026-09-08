from service import UserService


def get_user(repo, user_id: str) -> dict:
    user = UserService(repo).get_user(user_id)
    return {"id": user.id, "active": user.active}
