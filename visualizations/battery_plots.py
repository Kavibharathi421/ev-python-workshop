import numpy as np
from .style import bars, chart, GREEN, GOLD


def capacity_chart(capacity, available):
    return bars("Energy in the pack", "Battery energy", "Energy (kWh)",
                ["Full capacity", "Available now"], [capacity, available])


def power_chart(voltage, current):
    fig, ax = chart("Voltage × current = power", "Current (A)", "Electrical power (kW)")
    x = np.linspace(0, 300, 100)
    ax.plot(x, voltage * x / 1000, color=GREEN, label=f"{voltage} V pack")
    ax.scatter([current], [voltage * current / 1000], color=GOLD, s=70, zorder=3, label="Your setting")
    ax.legend(frameon=False)
    return fig
