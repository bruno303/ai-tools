# Task: investigate session expiry

Some sessions expire erratically, either too early or not at all, for certain
datetime inputs.

Investigate the existing session package modules (`auth.py`, `clock.py`, and
`store.py`) and fix the root cause so idle-expiry behavior is consistent and
deterministic around the configured idle limit. Preserve the existing public
API.
