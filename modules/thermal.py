import numpy as np
from .validation import check


def simulate(initial, ambient, cooling, load, minutes=60):
    check(initial, "Initial temperature", minimum=-40, maximum=100)
    check(ambient, "Ambient temperature", minimum=-40, maximum=60)
    check(cooling, "Cooling level", maximum=100)
    check(load, "Battery load", maximum=200)
    check(minutes, "Duration", positive=True)
    time = np.linspace(0, minutes, 241)
    # Toy heat balance: load adds heat; cooling increases heat transfer to ambient.
    heating = 0.012 * load  # degrees C per minute
    k = 0.008 + 0.072 * cooling / 100  # per minute
    equilibrium = ambient + heating / k
    temperature = equilibrium + (initial - equilibrium) * np.exp(-k * time)
    return time, temperature


def status(temperature):
    return ("Normal Temperature" if temperature < 35 else "Warm" if temperature < 45
            else "High Temperature" if temperature < 55 else "Critical")
