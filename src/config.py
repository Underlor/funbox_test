import os


REQUIRED = os.environ.__getitem__
OPTIONAL = os.environ.get


class CONFIG:
    REDIS_URL = OPTIONAL("REDIS_URL", "redis://localhost")
    LISTEN_PORT = OPTIONAL("LISTEN_PORT", 8000)
    FLUSH_DB = bool(OPTIONAL("FLUSH_DB", False))
