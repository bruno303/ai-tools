from datetime import timedelta

class SessionAuth:
    def __init__(self, store, clock, idle_limit=timedelta(minutes=30)):
        self.store = store
        self.clock = clock
        self.idle_limit = idle_limit

    def create(self, session_id, last_activity=None):
        self.store.put(session_id, last_activity or self.clock.now())

    def is_expired(self, session_id):
        last_activity = self.store.get(session_id)
        if last_activity is None:
            return True
        elapsed = self.clock.now() - last_activity
        return elapsed >= self.idle_limit
