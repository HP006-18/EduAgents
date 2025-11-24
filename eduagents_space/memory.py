import time, uuid
class MemoryBank:
    def __init__(self):
        # simple in-memory store: dict of session_id -> list of entries
        self.store = {}

    def create(self, obj):
        sid = str(uuid.uuid4())
        self.store[sid] = {'created_at': time.time(), 'data': obj, 'entries': []}
        return sid

    def append(self, sid, obj):
        if sid in self.store:
            self.store[sid]['entries'].append(obj)
            return True
        return False

    def get(self, sid):
        return self.store.get(sid)

    def clear(self):
        self.store = {}
