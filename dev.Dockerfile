FROM gorialis/discord.py:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY .env.local .
COPY --link src ./src

COPY db ./db

# gcc for compiling libsql bindings
# npm for nodemon (file watcher)
RUN apt-get update && apt-get install -y gcc npm
RUN pip install -r requirements.txt
RUN npm i -g nodemon

CMD ["nodemon","-L", "--watch", "src", "--watch", "db/models", "--exec", "python","src/main.py"]
