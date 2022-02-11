import json
from functools import lru_cache
from pathlib import Path

data_dir = Path(__file__).parent.joinpath("data")


@lru_cache()
def load_descriptions():
    with data_dir.joinpath("descriptions.json").open() as infile:
        descriptions = json.load(infile)
    return {
        f"{parameter} (Parameter)": {
            entry["value"]: "{value}: {description}".format(**entry)
            for entry in entries
        }
        for parameter, entries in descriptions.items()
    }
