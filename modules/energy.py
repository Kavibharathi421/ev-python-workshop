from .validation import check


def calculate(energy, inverter, motor, gear):
    check(energy, "Battery energy")
    values = [energy]
    for name, efficiency in zip(("Inverter", "Motor", "Gear"), (inverter, motor, gear)):
        check(efficiency, f"{name} efficiency", maximum=100)
        values.append(values[-1] * efficiency / 100)
    losses = [values[i] - values[i + 1] for i in range(3)]
    return values, losses
