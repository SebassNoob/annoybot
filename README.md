# Annoybot

This is the 2.0 rewrite for annoybot. ([<= 1.9.0 repo](https://github.com/SebassNoob/bot))

Built with discord.py and Turso.

## About
A discord.py bot primarily used to annoy your friends, harmlessly.

Highlights (Most used)
- roast: roast your friends with some dank roasts
- ghosttroll: ghost ping your friends in 3 different channels
- playnoise: play a stupid noise into your voice channel
- autoresponse: automatically respond to certain keywords
- ratio: produces a classic twitter ratio to ratio your friends
- And so much more! We have games, trolling, memes, dark jokes, we have it all!

Why wait? Piss your friends off now!

## Setup
Requirements:
```
docker && docker compose
GNU Make
```

Pre-run:

- Create a file named ``.env.local`` and set ``TOKEN=your_token``

Run:
```sh
source venv/bin/activate || venv\Scripts\activate # (macOS/linux OR windows)
make run
make init_db # skip if db is initialised already
make migrate # handles alembic upgrades
```
format: ``make black`` :)

alembic revision: ``alembic revision -m "my_revision"``
