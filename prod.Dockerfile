FROM gorialis/discord.py:3.10-alpine-minimal

WORKDIR /app

COPY requirements.txt .
COPY .venv .
COPY .env.local .
COPY --link src ./src

COPY db ./db

RUN pip install -r requirements.txt

CMD ["python", "src/main.py", "--prod"]
