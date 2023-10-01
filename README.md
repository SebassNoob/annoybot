# Annoybot

This is the 2.0 rewrite for annoybot. ([<= 1.9.0 repo](https://github.com/SebassNoob/bot))

Built with discord.py, Redis and Turso.

## About
A discord.py bot primarily used to annoy your friends, harmlessly.

Highlights (Most used)
- roast: roast your friends with some dank roasts
- ghosttroll: ghost ping your friends in 3 different channels
- playnoise: play a stupid noise into your voice channel
- autoresponse: automatically respond to certain keywords
- ratio: produces a classic twitter ratio to ratio your friends
- And so much more! We have games, trolling, memes, dark jokes, it's all here!

Why wait? Piss your friends off now!

### Architecture

DONE:
- Automatically sharded bot on the server
- Turso primary db (sin)

TODO:
- Redis caching on local machine
- Replication to secondary


## Setup

### Requirements:
```
docker
GNU Make
alembic

# optional 
python (venv)
pip
```

### Setup:

- Rename ``.env.local.example`` to ``.env.local``
- Set the required values
- Run ``make migrate`` (Alembic, preferred) or ``make init_db`` (manual)

### Run:
```sh
# optional: activate venv to isolate python env
source venv/bin/activate || venv\Scripts\activate # (macOS/linux || windows)
make run # docker compose down and up
make migrate # handles alembic upgrades
```

### Misc commands
format: ``make black`` :)

alembic revision: 

make changes to the ``db/models/`` directory. Once done, run ``make revise`` (Doing ``alembic revision -m "..."`` will not work with libsql) to autogenerate a revision with alembic.
