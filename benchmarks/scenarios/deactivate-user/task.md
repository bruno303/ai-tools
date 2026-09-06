# Task: add user deactivation

Add support for deactivating users across the existing service and API layers.

Requirements:

- `UserService.deactivate_user(user_id)` must load the user from the repository, mark it inactive, persist the updated user, and return it.
- Deactivation must be idempotent: deactivating an already inactive user succeeds and keeps it inactive.
- Unknown users must raise the existing `UserNotFound` exception.
- Add an API-level `deactivate_user(repo, user_id)` function that delegates through `UserService` and returns a dictionary with the user's `id` and `active` state.
- Preserve existing behavior and project structure.

Add or update tests as appropriate.
