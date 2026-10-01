from .style import chart, GREEN, GOLD


def energy_flow(values, losses):
    fig, ax = chart("Where the battery energy goes", "Conversion stage", "Energy (kWh)")
    ax.plot(range(4), values, color=GREEN, linewidth=3, marker="o", markersize=9)
    ax.fill_between(range(4), values, color=GREEN, alpha=0.08)
    for i, value in enumerate(values):
        ax.annotate(f"{value:.2f} kWh", (i, value), xytext=(0, 12), textcoords="offset points", ha="center")
        if i:
            # Downward branches show the energy diverted at each conversion.
            midpoint = (values[i-1] + value) / 2
            ax.annotate("", xy=(i-0.5, max(values[0]*0.23, midpoint-values[0]*0.20)),
                        xytext=(i-0.5, midpoint),
                        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
            ax.text((i-0.5)/3, 0.1, f"Loss: {losses[i-1]:.2f} kWh",
                    transform=ax.transAxes, ha="center", color="#97651D")
    ax.set_xticks(range(4), ["Battery", "Inverter", "Motor", "Gear → wheels"])
    ax.set_ylim(0, max(values[0] * 1.25, 1))
    return fig
