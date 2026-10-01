import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GREEN = "#236448"
GOLD = "#D49A36"


def chart(title, xlabel, ylabel):
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "text.color": "#24352E",
                         "axes.labelcolor": "#485A50", "axes.edgecolor": "#D8E0DB"})
    fig, ax = plt.subplots(figsize=(8, 3.8), layout="constrained")
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(axis="y", alpha=0.15)
    ax.set_axisbelow(True)
    return fig, ax


def line(title, xlabel, ylabel, x, y):
    fig, ax = chart(title, xlabel, ylabel)
    ax.plot(x, y, color=GREEN, linewidth=2.5)
    return fig


def bars(title, xlabel, ylabel, labels, values):
    fig, ax = chart(title, xlabel, ylabel)
    rects = ax.bar(labels, values, color=[GREEN, GOLD, "#73A58B", "#B4CDBE"][:len(values)], width=0.55)
    ax.bar_label(rects, fmt="%.2f", padding=4)
    ax.set_ylim(0, max(max(values) * 1.22, 1))
    return fig
