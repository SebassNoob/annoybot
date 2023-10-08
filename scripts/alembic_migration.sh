
source $(dirname $0)/load_env.sh


if [ "$1" == "--prod" ]; then 
  PROD_URL="sqlite+libsql:\/\/$PROD_DB_LOC"
  echo "Running alembic migrations in production mode $PROD_URL"
  sed "s|sqlite+libsql:\/\/localhost:8080|${PROD_URL}|" alembic.ini > alembic.ini.tmp

  alembic -c alembic.ini.tmp upgrade head
  rm alembic.ini.tmp
    
else
  echo "Running alembic migrations in dev mode"
  
  alembic -c alembic.ini upgrade head

fi

