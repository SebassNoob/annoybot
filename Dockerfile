FROM gorialis/discord.py:3.10-alpine-minimal

WORKDIR /app

COPY requirements.txt .
COPY .env.local .
COPY --link src ./src

RUN pip install -r requirements.txt
RUN apk add --update npm
RUN npm i -g nodemon

CMD ["nodemon","-L", "--watch", "src", "--exec", "python","src/main.py"]
