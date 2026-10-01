from .validation import check


def calculate(capacity, start, target, power, efficiency, price):
    check(capacity, "Capacity", positive=True)
    check(start, "Starting SOC", maximum=100)
    check(target, "Target SOC", maximum=100)
    if target < start:
        raise ValueError("Target SOC cannot be less than starting SOC. Increase the target or reduce the starting SOC.")
    check(power, "Charger power", positive=True)
    check(efficiency, "Charging efficiency", maximum=100, positive=True)
    check(price, "Electricity price")
    required = capacity * (target - start) / 100
    grid = required / (efficiency / 100)
    return {"required_kwh": required, "grid_kwh": grid,
            "ideal_hours": required / power, "hours": grid / power,
            "cost_inr": grid * price}
