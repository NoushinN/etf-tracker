from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_watchlist() -> list[dict]:
    return load_yaml("config/watchlist.yaml")["funds"]


def load_scoring() -> dict:
    return load_yaml("config/scoring.yaml")


