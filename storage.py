import json
import os
import fcntl
import tempfile

DATA_FILE = os.path.expanduser("~/.theater_mgr.json")
LOCK_FILE = os.path.expanduser("~/.theater_mgr.lock")

VALID_TYPES = ["话剧", "音乐剧", "儿童剧", "相声", "杂技"]


def _default_data():
    return {"shows": []}


def load_data():
    if not os.path.exists(DATA_FILE):
        return _default_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    dir_name = os.path.dirname(DATA_FILE)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


class FileLock:
    def __init__(self):
        self.lock_fd = None

    def __enter__(self):
        self.lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        self.lock_fd.close()
        self.lock_fd = None


def atomic_transaction(func):
    def wrapper(*args, **kwargs):
        with FileLock():
            data = load_data()
            result = func(data, *args, **kwargs)
            save_data(data)
            return result
    return wrapper
