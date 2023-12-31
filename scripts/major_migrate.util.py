import sys
import os
import sqlite3


def get_db_connection(db_path):
    if not os.path.exists(db_path):
        print("DB file not found: {}".format(db_path))
        sys.exit(1)
    return sqlite3.connect(db_path)


server_conn = get_db_connection("serverSettings.db")
user_conn = get_db_connection("userSettings.db")

os.mkdir("dump")

# autoresponse table
res = server_conn.execute(
    "SELECT id, autoresponse_content FROM serverSettings"
).fetchall()

for row in res:
    server_id: int = row[0]
    autores_dict: dict[str, str] = eval(row[1])

    with open("dump/autoresponse_dump.sql", "a", encoding="utf-8") as f:
        for key, value in autores_dict.items():
            k = key.replace("'", "''").__repr__().replace("\\", "")
            k = f"'{k[1:-1]}'"
            v = value.replace("'", "''").__repr__().replace("\\", "")
            v = f"'{v[1:-1]}'"
            f.write(
                f"INSERT INTO autoresponse (server_id, msg, response) VALUES ({server_id!r}, {k}, {v});\n"
            )

# server_settings table
res = server_conn.execute("SELECT id, autoresponse FROM serverSettings").fetchall()
for row in res:
    server_id: int = row[0]
    autores_on: bool = bool(row[1])

    with open("dump/server_settings_dump.sql", "a", encoding="utf-8") as f:
        f.write(
            f"INSERT INTO server_settings (id, autoresponse_on) VALUES ({server_id!r}, {autores_on!r});\n"
        )

# user_settings table
res = user_conn.execute("SELECT * FROM userSettings").fetchall()
for row in res:
    user_id = row[0]
    color = row[1]
    family_friendly = bool(row[2])
    sniped = bool(row[3])
    block_dms = bool(row[4])
    with open("dump/user_settings_dump.sql", "a", encoding="utf-8") as f:
        f.write(
            f"INSERT INTO user_settings (id, color, family_friendly, sniped, block_dms) VALUES ({user_id!r}, {color!r}, {family_friendly!r}, {sniped!r}, {block_dms!r});\n"
        )


# user_server table
res = server_conn.execute("SELECT id, blacklist FROM serverSettings").fetchall()
for row in res:
    server_id: int = row[0]
    blacklist: list[int] = eval(row[1])
    for user_id in blacklist:
        with open("dump/user_server_dump.sql", "a", encoding="utf-8") as f:
            f.write(
                f"INSERT INTO user_server (server_id, user_id, blacklist) VALUES ({server_id!r}, {user_id!r}, 1);\n"
            )


server_conn.close()
user_conn.close()
