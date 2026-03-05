"""
事件系统 - JSONL 事件溯源基础设施
"""
import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterator, List, Optional, Union

if os.name == 'nt':
    import msvcrt
    fcntl = None
else:
    import fcntl
    msvcrt = None


@dataclass
class Event:
    type: str
    timestamp: str
    seq: int = 0
    run_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, event_type: str, run_id: str = "", **data) -> "Event":
        return cls(
            type=event_type,
            timestamp=datetime.now().astimezone().isoformat(),
            run_id=run_id,
            data=data,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(',', ':'))

    @classmethod
    def from_json(cls, line: str) -> "Event":
        return cls(**json.loads(line))


@dataclass
class ArtifactRef:
    ref: str
    sha256: str
    size: int
    mime: str = "application/octet-stream"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


SENSITIVE_KEYS = {
    'api_key', 'apikey', 'api-key', 'api_token', 'secret', 'secret_key',
    'password', 'passwd', 'token', 'access_token', 'credential', 'auth',
}
SAFE_KEYS = {'token_usage', 'prompt_tokens', 'completion_tokens', 'total_tokens'}


def is_sensitive_key(key: str) -> bool:
    return key.lower() not in SAFE_KEYS and key.lower() in SENSITIVE_KEYS


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in data.items():
        if is_sensitive_key(key):
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value)
        elif isinstance(value, list):
            result[key] = [sanitize_dict(v) if isinstance(v, dict) else v for v in value]
        else:
            result[key] = value
    return result


def sanitize_event(event: Event) -> Event:
    return Event(
        type=event.type, timestamp=event.timestamp, seq=event.seq,
        run_id=event.run_id, data=sanitize_dict(event.data),
    )


class FileLock:
    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self._fd = None

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._fd = open(self.lock_path, 'w')
            if os.name == 'nt':
                start = time.time()
                while True:
                    try:
                        msvcrt.locking(self._fd.fileno(), msvcrt.LK_NBLCK, 1)
                        return True
                    except IOError:
                        if not blocking or (timeout and (time.time() - start) >= timeout):
                            return False
                        time.sleep(0.1)
            else:
                flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if not blocking else 0)
                try:
                    fcntl.flock(self._fd.fileno(), flags)
                    return True
                except BlockingIOError:
                    return False
        except Exception:
            if self._fd:
                self._fd.close()
                self._fd = None
            raise

    def release(self):
        if self._fd:
            try:
                if os.name == 'nt':
                    msvcrt.locking(self._fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self._fd.fileno(), fcntl.LOCK_UN)
            finally:
                self._fd.close()
                self._fd = None


class RunLock:
    def __init__(self, run_dir: Path):
        self._lock = FileLock(Path(run_dir) / "locks" / "run.lock")

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        return self._lock.acquire(blocking, timeout)

    def release(self):
        self._lock.release()


class EventWriter:
    def __init__(self, run_dir: Path, sanitize: bool = True):
        self.run_dir = Path(run_dir)
        self.events_file = self.run_dir / "events.jsonl"
        self.sanitize = sanitize
        self._seq = 0
        self._lock = Lock()
        if self.events_file.exists():
            for line in open(self.events_file, 'r', encoding='utf-8'):
                if line.strip():
                    try:
                        e = Event.from_json(line.strip())
                        self._seq = max(self._seq, e.seq)
                    except Exception:
                        pass

    def write(self, event: Event) -> Event:
        with self._lock:
            self._seq += 1
            event.seq = self._seq
            if self.sanitize:
                event = sanitize_event(event)
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.events_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
                f.flush()
                os.fsync(f.fileno())
            return event

    def emit(self, event_type: str, run_id: str = "", **data) -> Event:
        return self.write(Event.create(event_type, run_id, **data))


class EventReader:
    def __init__(self, run_dir: Path):
        self.events_file = Path(run_dir) / "events.jsonl"

    def read_all(self) -> List[Event]:
        events = []
        if self.events_file.exists():
            for line in open(self.events_file, 'r', encoding='utf-8'):
                if line.strip():
                    try:
                        events.append(Event.from_json(line.strip()))
                    except json.JSONDecodeError:
                        pass
        return events

    def iter_events(self) -> Iterator[Event]:
        if self.events_file.exists():
            for line in open(self.events_file, 'r', encoding='utf-8'):
                if line.strip():
                    try:
                        yield Event.from_json(line.strip())
                    except json.JSONDecodeError:
                        pass

    def get_last_event(self, event_type: str = None) -> Optional[Event]:
        events = self.read_all()
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-1] if events else None


class ArtifactStore:
    MIME_TYPES = {'.json': 'application/json', '.txt': 'text/plain', '.md': 'text/markdown', '.py': 'text/x-python'}

    def __init__(self, run_dir: Path):
        self.artifacts_dir = Path(run_dir) / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, content: Union[str, bytes, dict, list], mime: str = None) -> ArtifactRef:
        path = self.artifacts_dir / name
        if isinstance(content, (dict, list)):
            content_bytes = json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
            mime = mime or 'application/json'
        elif isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        mime = mime or self.MIME_TYPES.get(path.suffix.lower(), 'application/octet-stream')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(content_bytes)
            f.flush()
            os.fsync(f.fileno())
        return ArtifactRef(ref=f"artifacts/{name}", sha256=sha256, size=len(content_bytes), mime=mime)

    def read(self, name: str) -> bytes:
        path = self.artifacts_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {name}")
        return path.read_bytes()

    def read_json(self, name: str) -> Any:
        return json.loads(self.read(name).decode('utf-8'))

    def verify(self, ref: ArtifactRef) -> bool:
        name = ref.ref.replace("artifacts/", "")
        path = self.artifacts_dir / name
        if not path.exists():
            return False
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest() == ref.sha256 and len(content) == ref.size


def create_run_context(run_dir: Path) -> tuple:
    return EventWriter(run_dir), ArtifactStore(run_dir), RunLock(run_dir)
