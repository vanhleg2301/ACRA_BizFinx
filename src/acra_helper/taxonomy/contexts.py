from datetime import date
from typing import Optional

PPE_AXIS = "sg-as:ClassesOfPropertyPlantAndEquipmentAxis"
PPE_MEMBERS = [
    "MachineryAndOtherEquipmentMember",
    "ComputerOfficeEquipmentAndFurnitureFixturesAndFittingsMember",
    "ConstructionInProgressMember",
    "OtherPropertyPlantAndEquipmentMember",
]


def build_contexts(fye: date) -> dict[str, dict]:
    """
    Generate the standard 17 ACRA contexts for a company with the given fiscal year end.

    Produces:
    - 2 duration contexts (current year, prior year)
    - 3 instant contexts without dimension (current, prior, prior-2)
    - 12 instant contexts with PP&E dimension (4 members × 3 years)
    """
    cur_end = fye
    cur_start = date(cur_end.year, 1, 1)
    prior_end = date(cur_end.year - 1, cur_end.month, cur_end.day)
    prior_start = date(prior_end.year, 1, 1)
    prior2_end = date(cur_end.year - 2, cur_end.month, cur_end.day)

    def _fmt(d: date) -> str:
        return d.strftime("%Y%m%d")

    contexts: dict[str, dict] = {}

    for start, end in [(cur_start, cur_end), (prior_start, prior_end)]:
        key = f"fromto_{_fmt(start)}_{_fmt(end)}"
        contexts[key] = {
            "period": {"type": "duration", "start": start.isoformat(), "end": end.isoformat()},
            "dimension": None,
        }

    for d in [cur_end, prior_end, prior2_end]:
        key = f"asof_{_fmt(d)}"
        contexts[key] = {
            "period": {"type": "instant", "date": d.isoformat()},
            "dimension": None,
        }

    for d in [cur_end, prior_end, prior2_end]:
        for member in PPE_MEMBERS:
            key = f"asof_{_fmt(d)}_{member}"
            contexts[key] = {
                "period": {"type": "instant", "date": d.isoformat()},
                "dimension": {"axis": PPE_AXIS, "member": f"sg-as:{member}"},
            }

    return contexts
