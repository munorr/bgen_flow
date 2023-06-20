from pathlib import Path


def get(filename: str) -> Path:
    return Path(__file__).parent.joinpath(filename)

