import numpy as np
from .style import chart, GREEN, GOLD


def charging_curve(start, target, hours):
    fig, ax = chart("Charging session · constant power model", "Elapsed time (hours)", "SOC (%)")
    if hours == 0:
        ax.scatter([0], [start], color=GREEN)
    else:
        ax.plot(np.linspace(0, hours, 100), np.linspace(start, target, 100), color=GREEN, linewidth=3)
        ax.scatter([hours], [target], color=GOLD, zorder=3)
    ax.set_ylim(0, 105)
    return fig
