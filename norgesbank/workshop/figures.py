"""Illustrations for the workshop deck. Open data only (SSB), so the deck can be published."""

import io
import itertools
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

INK, GOLD, RED, PAPER = "#2b2118", "#b8860b", "#8b1e1e", "#f3ead7"
OUT = Path(__file__).parent.parent / "img"
plt.rcParams.update(
    {
        "font.family": "Iowan Old Style",
        "font.size": 20,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "svg.fonttype": "none",
    }
)


def kpi_chart() -> None:
    url = "https://data.ssb.no/api/pxwebapi/v2/tables/14706/data?lang=en&outputformat=csv&outputFormatParams=UseCodes&valueCodes[KPIavledetSerie]=KPI-JAE&valueCodes[ContentsCode]=Tolvmanedersendring&valueCodes[Tid]=*"
    df = pd.read_csv(io.StringIO(requests.get(url).text), na_values=".")
    s = pd.to_numeric(df.filter(regex=r"\d{4}M\d{2}").iloc[0], errors="coerce").dropna()
    s.index = pd.PeriodIndex(
        [c.split()[-1].replace("M", "-") for c in s.index], freq="M"
    ).to_timestamp()
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.axhline(2, color=GOLD, lw=2, ls=(0, (6, 4)))
    ax.text(s.index[0], 2.15, "Mål: 2 %", color=GOLD, fontsize=18)
    ax.plot(s.index, s.values, color=INK, lw=2.5)
    last = s.index[-1]
    ax.annotate(
        f"{s.iloc[-1]:.1f} %".replace(".", ","),
        (last, s.iloc[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=18,
    )
    ax.set_ylabel("KPI-JAE, 12-mnd. endring (%)", fontsize=17)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK)
    ax.grid(axis="y", color=INK, alpha=0.12)
    fig.savefig(OUT / "ws_kpi.svg", transparent=True, bbox_inches="tight")


def network(
    layers: list[int], labels: dict, name: str, highlight: int | None = None
) -> None:
    """Draw a feed-forward network. layers = number of nodes per layer."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    xs = [i / (len(layers) - 1) for i in range(len(layers))]
    pos = []
    for x, n in zip(xs, layers):
        h = min(1.0, 0.09 * (n - 1))  # height of the column of nodes
        pos.append(
            [(x, 0.5 + h / 2 - h * j / max(n - 1, 1)) for j in range(n)]
            if n > 1
            else [(x, 0.5)]
        )
    for a, b in itertools.pairwise(pos):
        for p in a:
            for q in b:
                ax.plot(
                    [p[0], q[0]], [p[1], q[1]], color=GOLD, lw=1.2, alpha=0.55, zorder=1
                )
    for li, layer in enumerate(pos):
        for p in layer:
            ax.scatter(
                *p,
                s=520,
                color=RED if li == highlight else PAPER,
                edgecolor=INK,
                lw=2,
                zorder=3,
            )
    for li, text in labels.items():
        ax.text(xs[li], -0.11, text, ha="center", va="top", fontsize=26)
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(-0.3, 1.08)
    ax.axis("off")
    # opaque background: the diagrams are stacked on top of each other in the deck
    fig.savefig(OUT / name, facecolor=PAPER, bbox_inches="tight")


kpi_chart()
network([12, 1], {0: "12 siste måneder", 1: "neste måned"}, "ws_net_ar.svg")
network(
    [14, 3, 1],
    {0: "konsumgrupper", 1: "3 faktorer", 2: "neste måned"},
    "ws_net_factor.svg",
    highlight=1,
)
network(
    [14, 8, 1],
    {0: "konsumgrupper", 1: "skjult lag + ReLU", 2: "neste måned"},
    "ws_net_mlp.svg",
    highlight=1,
)
