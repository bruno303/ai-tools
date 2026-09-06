from dataclasses import dataclass


class UserNotFound(Exception):
    pass


@dataclass
class User:
    id: str
    active: bool = True
