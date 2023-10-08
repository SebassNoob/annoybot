
# create dump
python scripts/major_migrate.util.py

# load dump
sqlite3 ./db/local.db/iku.db/dbs/default/data -cmd ".read dump/server_settings_dump.sql" ".read dump/autoresponse_dump.sql" ".read dump/user_settings_dump.sql" ".read dump/user_server_dump.sql"

# clean
rm -rf ./dump

