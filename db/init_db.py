import sys
from client import make_engine
from models import (
    Autoresponse,
    Base,
    Hello,
    ServerSettings,
    Snipe,
    UserServer,
    UserSettings,
)

from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

import os
import dotenv

dotenv.load_dotenv(f"{os.getcwd()}/.env")
dotenv.load_dotenv(f"{os.getcwd()}/.env.local")


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
        session.close()


if __name__ == "__main__":
    # mapping of command line arguments to functions
    mapping = {"init": init_db, "drop": drop_db, "test": test_db}

    checks = [len(sys.argv) >= 2, sys.argv[1] in mapping.keys()]

    # check if the command line arguments are valid
    if not all(checks):
        print("Usage: python init_db.py <init|drop|test> [--prod]")
        sys.exit(1)
    # check if the bot is running in production mode
    loc = (
        os.getenv("PROD_DB_LOC")
        if len(sys.argv) == 3 and sys.argv[2] == "--prod"
        else os.getenv("DEV_DB_LOC")
    )

    # make the engine
    engine = make_engine(loc=loc, echo=True, debug=True)
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
