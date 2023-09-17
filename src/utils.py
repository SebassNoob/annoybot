import csv


def read_csv(path: str) -> list:
    """
    Reads a 2 column csv file and returns a list of dicts with the first column as the key and the second column as the value
    """
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
