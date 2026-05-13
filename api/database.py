import os
import re
import ssl
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL não configurado")
    url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
    url = re.sub(r"[&?]sslmode=[^&]*", "", url)
    url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    url = url.replace("postgres://", "postgresql+pg8000://", 1)
    ssl_ctx = ssl.create_default_context()
    return create_engine(
        url,
        pool_size=5,
        max_overflow=10,
        connect_args={"ssl_context": ssl_ctx},
    )
