
source $(dirname $0)/load_env.sh


if [ "$1" == "--prod" ]; then 
  PROD_URL="sqlite+libsql:\/\/$PROD_DB_LOC"
  echo "Running alembic migrations in production mode"
  sed "s|sqlite+libsql:\/\/localhost:8080|${PROD_URL}|" alembic.ini > alembic.ini.tmp

  alembic -c alembic.ini.tmp upgrade head

    
else
  DEV_URL="sqlite+libsql:\/\/$DEV_DB_LOC"
  echo "Running alembic migrations in production mode"
  sed "s|sqlite+libsql:\/\/localhost:8080|${DEV_URL}|" alembic.ini > alembic.ini.tmp

  alembic -c alembic.ini.tmp upgrade head

fi

rm alembic.ini.tmp