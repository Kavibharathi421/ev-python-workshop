from .battery import calculate as battery
from .validation import check

CONDITIONS = {"City": 1.0, "Highway": 1.05, "Traffic": 1.15, "Aggressive Driving": 1.30}


def calculate(capacity, soc, consumption, speed, ac_kw, condition):
    energy = battery(capacity, soc)["available_kwh"]
    check(consumption, "Consumption", positive=True)
    check(speed, "Speed", positive=True)
    check(ac_kw, "AC power")
    if condition not in CONDITIONS:
        raise ValueError("Choose a listed driving condition.")
    # A teaching heuristic referenced to 50 km/h, not a fitted road-load model.
    speed_factor = 0.75 + 0.25 * (speed / 50) ** 2
    effective = consumption * CONDITIONS[condition] * speed_factor + ac_kw / speed
    return {"available_kwh": energy, "consumption_kwh_km": effective,
            "range_km": energy / effective}
