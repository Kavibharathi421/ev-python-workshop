from .validation import check


def calculate(mass, speed, efficiency, events):
    check(mass, "Vehicle mass")
    check(speed, "Vehicle speed")
    check(efficiency, "Regeneration efficiency", maximum=100)
    check(events, "Braking events")
    if int(events) != events:
        raise ValueError("Braking events must be a whole number.")
    kinetic_j = 0.5 * mass * (speed / 3.6) ** 2
    recovered = kinetic_j * efficiency / 100 / 3_600_000
    return {"kinetic_j": kinetic_j, "kinetic_kwh": kinetic_j / 3_600_000,
            "recovered_kwh": recovered, "total_kwh": recovered * events}
