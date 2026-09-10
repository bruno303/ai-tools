# Task: implement a sliding-window limiter

`FixedWindowLimiter` is complete, but `SlidingWindowLimiter` is only a
scaffold and its tests fail.

Implement `SlidingWindowLimiter` with the same constructor and `allow(key)`
API as the fixed-window limiter. It must allow at most `limit` requests for a
key in any rolling `window_seconds` interval. Use the injected clock so the
behavior is deterministic, and preserve the existing fixed-window behavior.
