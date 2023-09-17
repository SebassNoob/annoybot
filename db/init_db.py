import sys
from client import make_engine
from models.base import Base
from models.hello import Hello
from sqlalchemy.orm import Session

from sqlalchemy.engine import Engine


def init_db(engine: Engine):
    """
    Creates all the tables in the database
    """

    Base.metadata.create_all(engine)


def drop_db(engine: Engine):
    """
    Drops all the tables in the database
    """
    Base.metadata.drop_all(engine)


def test_db(engine: Engine):
    """
    Attempts to write and read a test value from table "hello"
    """
    new = Hello(msg="Hello World!")
    with Session(engine) as session:
        session.add(new)
        session.commit()
        res = session.query(Hello).all()
        print(res)


if __name__ == "__main__":
    engine = make_engine(echo=True, debug=True)
    # mapping of command line arguments to functions
    mapping = {"init": init_db, "drop": drop_db, "test": test_db}

    checks = [len(sys.argv) == 2, sys.argv[1] in mapping.keys()]

    # check if the command line arguments are valid
    if not all(checks):
        print("Usage: python init_db.py <init|drop|test>")
        sys.exit(1)

    try:
        # run the corresponding function
        mapping[sys.argv[1]](engine)
    except Exception as e:
        print(e)
        engine.dispose()
        sys.exit(1)

    # close the engine and exit
    engine.dispose()
    sys.exit(0)
