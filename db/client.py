from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# SQLAlchemy engine
def make_engine(
    *, loc: str = "localhost:8080", echo: bool = False, debug: bool = False
) -> Engine:
    url = f"sqlite+libsql://{loc}"
    engine = create_engine(url, echo=echo, echo_pool=debug)
    return engine
