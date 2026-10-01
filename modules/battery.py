from .validation import check


def calculate(capacity, soc, voltage=400, current=100):
    check(capacity, "Battery capacity", positive=True)
    check(soc, "SOC", maximum=100)
    check(voltage, "Voltage", positive=True)
    check(current, "Current")
    return {"available_kwh": capacity * soc / 100,
            "power_kw": voltage * current / 1000}
