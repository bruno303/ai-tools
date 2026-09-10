class SessionStore:
    def __init__(self):
        self._sessions = {}

    def put(self, session_id, last_activity):
        self._sessions[session_id] = last_activity

    def get(self, session_id):
        return self._sessions.get(session_id)
