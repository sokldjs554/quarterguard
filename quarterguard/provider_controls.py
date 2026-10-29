"""Atomic attempt reservations. Failed/unknown network outcomes still consume quota."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import time
import uuid

class Blocked(RuntimeError):
    pass

class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS calls (id TEXT PRIMARY KEY, provider TEXT, target TEXT, ts REAL, day TEXT, outcome TEXT)')
    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            with db: yield db
        finally: db.close()
    def reserve(self, provider, target, *, total, daily, cooldown):
        now = time.time(); day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            n, today, last = db.execute('SELECT COUNT(*), COALESCE(SUM(day=?),0), MAX(ts) FROM calls WHERE provider=?', (day, provider)).fetchone()
            if n >= total or today >= daily: raise Blocked('QUOTA_EXHAUSTED')
            if last is not None and now-last < cooldown: raise Blocked('COOLDOWN')
            rid = str(uuid.uuid4())
            db.execute('INSERT INTO calls VALUES (?,?,?,?,?,NULL)', (rid, provider, target, now, day))
        return rid
    def finish(self, rid, result):
        with self.db() as db: db.execute('UPDATE calls SET outcome=? WHERE id=?', (json.dumps(result, ensure_ascii=False), rid))
    def cached(self, provider, target, max_age=86400):
        with self.db() as db:
            rows = db.execute('SELECT outcome FROM calls WHERE provider=? AND target=? AND ts>? AND outcome IS NOT NULL ORDER BY ts DESC', (provider,target,time.time()-max_age)).fetchall()
        for (raw,) in rows:
            value = json.loads(raw)
            if value.get('status') == 'succeeded': return value
        return None
    def usage(self, provider):
        day = datetime.now(timezone.utc).date().isoformat()
        with self.db() as db:
            total,today = db.execute('SELECT COUNT(*), COALESCE(SUM(day=?),0) FROM calls WHERE provider=?',(day,provider)).fetchone()
        return {'attempts_total':total,'attempts_today_utc':today}
