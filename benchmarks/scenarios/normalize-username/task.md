# Task: normalize usernames consistently

The project exposes `normalize_username` in `usernames.py`.

Update the implementation so usernames are normalized consistently before use:

- surrounding whitespace must be ignored
- usernames must be lowercase
- a username that is empty after trimming is invalid and must raise `ValueError`

Keep the change focused and preserve the existing public function signature. Update or add tests as appropriate.
