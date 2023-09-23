import csv
from aiohttp import ClientSession
from typing import Any


def read_csv(path: str, *, as_dict=False) -> list[str] | list[dict[str, str]]:
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
        return [(r[0], r[1].replace(";", ",")) for r in reader]


def parse_txt(path: str) -> list[str]:
    """Reads a txt and returns a list of the lines"""
    with open(path, "r") as f:
        res = [r.replace("\n", "") for r in f.readlines()]
    return res


async def fetch_json(
    client: ClientSession, path: str, headers: dict[str, str]
) -> tuple[dict[Any, Any], int]:
    async with client.get(path, headers=headers) as response:
        return await response.json(), response.status
