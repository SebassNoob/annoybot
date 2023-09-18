import csv


def read_csv(path: str) -> list:
    """
    Reads a 2 column csv file and returns a list of dicts with the first column as the key and the second column as the value
    """
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_txt(path: str) -> list:
    """Reads a txt and returns a list of the lines"""
    with open(path, "r") as f:
        res = [r.replace("\n", "") for r in f.readlines()]
    return res


def changeff(string: str) -> str:
    to_replace = {
        "fuck": "f#k",
        "bitch": "bi##h",
        "shit": "sh#t",
        "ass": "a##",
        "bastard": "b#stard",
        "dick": "d##k",
        "penis": "pen#s",
        "vagina": "vag#na",
    }
    for old, new in to_replace.items():
        string = string.replace(old, new)

    return string
