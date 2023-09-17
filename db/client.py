from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# SQLAlchemy engine
def make_engine(echo: bool = False, debug: bool = False) -> Engine:
    url = "sqlite+libsql://127.0.0.1:8080"
    engine = create_engine(url, echo=echo, echo_pool=debug)
    return engine
