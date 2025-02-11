from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# SQLAlchemy engine
def make_engine(
    *, loc: str = "localhost:8080", echo: bool = False, debug: bool = False
) -> Engine:
    url = f"sqlite+libsql://{loc}"
    # WARNING: do not spawn a thread that can write to the database, only main thread can write
    engine = create_engine(
        url,
        echo=echo,
        echo_pool=debug,
        isolation_level="AUTOCOMMIT",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    return engine
