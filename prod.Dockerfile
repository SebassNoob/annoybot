FROM gorialis/discord.py:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY .env.local .
COPY --link src ./src

COPY db ./db

# gcc for compiling libsql bindings
RUN apt-get update && apt-get install -y gcc
RUN pip install -r requirements.txt

CMD ["python", "src/main.py", "--prod"]
