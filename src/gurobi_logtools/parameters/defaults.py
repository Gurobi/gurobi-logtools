import json
from functools import lru_cache
from pathlib import Path

data_dir = Path(__file__).parent.joinpath("data")


@lru_cache()
def load_defaults(version):
    version_file = data_dir.joinpath(f"{version}.json")
    if not version_file.exists():
        # Fall back to 1203 defaults
        version_file = data_dir.joinpath("1203.json")
    with version_file.open() as infile:
        return json.load(infile)
