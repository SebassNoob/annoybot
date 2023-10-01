
# this script is used to create a new alembic revision that does not conflict with libsql dialect

sed 's/sqlite+libsql:\/\/localhost:8080/sqlite:\/\/\/tmp.sqlite3/' alembic.ini > alembic.ini.tmp
touch tmp.sqlite3

alembic -c alembic.ini.tmp upgrade head

alembic -c alembic.ini.tmp revision --autogenerate -m "$1"

rm alembic.ini.tmp
rm tmp.sqlite3