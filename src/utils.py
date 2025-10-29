import csv
import json
from aiohttp import ClientSession
from typing import Any, Optional, Literal
import discord

from sqlalchemy import Engine
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import IntegrityError

from db.models import UserServer, UserSettings, ServerSettings, Autoresponse
import redis


def read_csv(path: str, *, as_dict=False) -> list[tuple[Any]] | list[dict[str, str]]:
    """
    Reads a 2 column csv file and returns a list of dicts with the first column as the key and the second column as the value (no headers)

    If as_dict is True, returns a list of dicts with the keys being the column names
    """
    with open(path, "r", encoding="utf-8") as f:
        if as_dict:
            reader = csv.DictReader(f)

            # replace ; with , for the values
            # iterate over reader for dicts (d) and iterate over d.items() to replace
            return [{k: v.replace(";", ",") for k, v in d.items()} for d in reader]

        reader = csv.reader(f)
        _ = next(reader)
        return [tuple(map(lambda val: val.replace(";", ","), r)) for r in reader]


def read_json(path: str) -> dict[Any, Any]:
    """Reads a json and returns the dict"""
    with open(path, "r", encoding="utf-8") as f:
        res: dict[Any, Any] = json.load(f)
    return res


def parse_txt(path: str) -> list[str]:
    """Reads a txt and returns a list of the lines"""
    with open(path, "r", encoding="utf-8") as f:
        res = [r.replace("\n", "") for r in f.readlines()]
    return res


async def fetch_json(
    client: ClientSession, path: str, headers: Optional[dict[str, str]] = None
) -> tuple[dict[Any, Any], int]:
    """Fetches a json from a path and returns the json and the status code"""
    async with client.get(path, headers=headers) as response:
        return await response.json(), response.status


class HDict(dict):
    """A dict that can be hashed"""

    def __hash__(self):
        return hash(frozenset(self.items()))


def add_user(
    user: discord.User | discord.Member, engine: Engine, with_server: bool = True
):
    """Adds a user to the database. WARNING: This assumes the user is not in the database already"""
    with Session(engine) as session:
        try:
            # First add UserSettings
            session.add(
                UserSettings(
                    id=user.id,
                    color="000000",
                    family_friendly=False,
                    sniped=True,
                    block_dms=False,
                )
            )
            session.flush()  # Flush to ensure UserSettings is in DB before adding UserServer

            if with_server:
                session.add(
                    UserServer(
                        user_id=user.id,
                        server_id=user.guild.id,
                        blacklist=False,
                    )
                )
            session.commit()
        except (IntegrityError, ValueError):
            # User or UserServer already exists, ignore the error
            # ValueError is raised by libsql for constraint violations
            session.rollback()


def check_usersettings_cache(
    *,
    user: discord.User | discord.Member,
    columns: list[Literal["id", "color", "family_friendly", "sniped", "block_dms"]],
    engine: Engine,
    redis_client: redis.Redis,
) -> list[Any]:
    """Checks if a user is in the cache. columns is a tuple of the columns in usersettings to check"""
    key = f"usersettings:{user.id}"
    res = redis_client.hmget(key, columns)
    if not all(res):
        # if not all columns are in the cache, get them from the db
        with Session(engine) as session:
            raw = (
                session.query(UserSettings)
                .filter(UserSettings.id == user.id)
                .one_or_none()
            )
            if raw is None:
                # if the user is not in the db, add them
                add_user(user, engine)
                raw = (
                    session.query(UserSettings).filter(UserSettings.id == user.id).one()
                )

            # add to cache
            redis_client.hset(
                key,
                mapping={
                    "id": raw.id,
                    "color": raw.color,
                    "family_friendly": str(raw.family_friendly),
                    "sniped": str(raw.sniped),
                    "block_dms": str(raw.block_dms),
                },
            )
            redis_client.expire(key, 60 * 30)  # expire after 30 minutes
        # return the columns from the db
        res = [getattr(raw, col) for col in columns]
    else:
        # parse bools which are stored as strings
        for idx, val in enumerate(res):
            if val in ("True", "False"):
                res[idx] = True if val == "True" else False

    return res


def page_query(q: Query):
    offset = 0
    while True:
        r = False
        for elem in q.limit(500).offset(offset):
            r = True
            yield elem
        offset += 500
        if not r:
            break
