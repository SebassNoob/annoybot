from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os


# SQLAlchemy engine
def make_engine(
    *, loc: str = "localhost:8080", echo: bool = False, debug: bool = False
) -> Engine:
    # Strip any protocol prefix from loc
    loc = loc.replace("https://", "").replace("http://", "").replace("wss://", "")

    # For Turso remote databases (.turso.io), add ?secure=true parameter
    if ".turso.io" in loc and "?" not in loc:
        loc = f"{loc}?secure=true"

    url = f"sqlite+libsql://{loc}"

    # For Turso databases, disable pooling to avoid stream expiration issues
    is_turso = ".turso.io" in loc

    # WARNING: do not spawn a thread that can write to the database, only main thread can write
    engine = create_engine(
        url,
        echo=echo,
        echo_pool=debug,
        connect_args={
            "check_same_thread": False,
            "auth_token": os.getenv("PROD_DB_TOKEN", None),
        },
        # For Turso, use NullPool to avoid connection reuse issues
        poolclass=(
            __import__("sqlalchemy.pool", fromlist=["NullPool"]).NullPool
            if is_turso
            else None
        ),
        pool_pre_ping=not is_turso,  # Disable pre-ping for Turso since we're using NullPool
    )
    return engine
