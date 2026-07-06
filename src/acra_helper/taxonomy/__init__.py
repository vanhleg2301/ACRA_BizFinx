import json
from pathlib import Path

_HERE = Path(__file__).parent


def load_calc_rules() -> dict[str, list[dict]]:
    return json.loads((_HERE / "calc_rules.json").read_text(encoding="utf-8"))


def load_fact_map_seed() -> dict:
    return json.loads((_HERE / "fact_map_seed.json").read_text(encoding="utf-8"))


def load_contexts_seed() -> dict:
    return json.loads((_HERE / "contexts_seed.json").read_text(encoding="utf-8"))
