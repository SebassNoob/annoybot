
# loads required environment variables
if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi
if [ -f .env.local ]; then
  export $(echo $(cat .env.local | sed 's/#.*//g'| xargs) | envsubst)
fi