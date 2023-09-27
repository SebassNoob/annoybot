import csv
import json
from aiohttp import ClientSession
from typing import Any, Optional
import discord

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import UserServer, UserSettings, ServerSettings, Autoresponse


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
            session.add(
                UserSettings(
                    id=user.id,
                    color="000000",
                    family_friendly=False,
                    sniped=True,
                    block_dms=False,
                )
            )
            if with_server:
                session.add(
                    UserServer(
                        user_id=user.id,
                        server_id=user.guild.id,
                        blacklist=False,
                    )
                )
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise Exception(e)
