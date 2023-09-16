import asyncio
import os
import sys
from client import create_client


async def init_db():
    """
    Reads all the files in the schemas directory and executes them
    """
    client = await create_client()
    fp = os.listdir(os.path.dirname(__file__) + "/schemas")
    print("\n")
    for f in fp:
        with open(os.path.dirname(__file__) + "/schemas/" + f, "r") as file:
            cmd = file.read()
            print(cmd)
            await client.execute(cmd)

    await client.close()


async def drop_db():
    """
    Reads all the files in the schemas directory and drops them based on the file name
    """
    client = await create_client()
    fp = os.listdir(os.path.dirname(__file__) + "/schemas")
    print("\n")
    for f in fp:
        with open(os.path.dirname(__file__) + "/schemas/" + f, "r") as file:
            # drops all tables (tables are named after the file name)
            cmd = (
                "DROP TABLE IF EXISTS "
                + os.path.splitext(os.path.basename(file.name))[0]
                + ";"
            )
            print(cmd)
            await client.execute(cmd)

    await client.close()


async def test_db():
    """
    Attempts to write and read a test value from table "hello"
    """
    client = await create_client()

    await client.execute("INSERT INTO hello (id, msg) VALUES (?, ?);", (None, "world"))
    result = await client.execute("SELECT * FROM hello;")
    print("\nResult:")
    print([row.asdict() for row in result.rows])
    await client.close()


if __name__ == "__main__":
    

    # mapping of command line arguments to functions
    mapping = {"init": init_db, "drop": drop_db, "test": test_db}

    checks = [len(sys.argv) == 2, sys.argv[1] in mapping.keys()]

    # check if the command line arguments are valid
    if not all(checks):
        print("Usage: python init_db.py <init|drop|test>")
        sys.exit(1)

    
    loop = asyncio.new_event_loop()
    try:
        # run the corresponding function
        loop.run_until_complete(mapping[sys.argv[1]]())
    except Exception as e:
        print(e)
        loop.close()
        sys.exit(1)

    # close the event loop and exit
    loop.close()
    sys.exit(0)
