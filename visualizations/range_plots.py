import numpy as np
from .style import line, bars
from modules.range import calculate, CONDITIONS


def soc_curve(soc, distance):
    x = np.linspace(0, max(distance, 1), 100)
    y = np.linspace(soc, 0, 100) if distance > 0 else np.zeros(100)
    return line("Battery state along your journey", "Distance (km)", "SOC (%)", x, y)


def comparison(capacity, soc, consumption, speed, ac):
    values = [calculate(capacity, soc, consumption, speed, ac, c)["range_km"] for c in CONDITIONS]
    return bars("Same EV, different driving conditions", "Driving condition", "Range (km)",
                ["City", "Highway", "Traffic", "Aggressive"], values)


def consumption_curve(energy):
    x = np.linspace(0.08, 0.4, 120)
    return line("Efficiency changes how far you go", "Total consumption (kWh/km)", "Range (km)", x, energy / x)
