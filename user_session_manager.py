import time
from collections import deque

class UserSessionManager:
    def __init__(self, max_history=5):
        self.sessions = {}
        self.max_history = max_history

    def add_message(self, user_id, role, content):
        if user_id not in self.sessions:
            self.sessions[user_id] = deque(maxlen=self.max_history)
        
        self.sessions[user_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

    def get_history(self, user_id):
        return list(self.sessions.get(user_id, []))

    def clear_history(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]