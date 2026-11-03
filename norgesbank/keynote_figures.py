"""Charts for the keynote, drawn from public data in the deck's palette."""

import itertools
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
import yaml

INK, GOLD, RED = "#2b2118", "#b8860b", "#8b1e1e"
OUT = Path(__file__).parent / "img"
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

LABELS = {
    "gpt2": "GPT-2",
    "davinci_002": "GPT-3",
    "gpt_3_5_turbo_instruct": "GPT-3.5",
    "gpt_4": "GPT-4",
    "o3_inspect": "o3",
    "gpt_5_2025_08_07_inspect": "GPT-5",
    "claude_opus_4_6_inspect": "Claude Opus 4.6",
    "claude_mythos_preview_early_inspect": "Claude Mythos (tidlig)",
}


def metr_chart(until: date, name: str) -> None:
    """One build stage: SOTA points released up to `until`, on the full chart's axes."""
    data = yaml.safe_load(
        requests.get("https://metr.org/assets/benchmark_results_1_1.yaml").text
    )["results"]
    all_rows = sorted(
        (v["release_date"], k, v["metrics"]["p50_horizon_length"]["estimate"] / 60)
        for k, v in data.items()
        if v["metrics"].get("is_sota")
    )
    rows = [r for r in all_rows if r[0] <= until]
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_facecolor("#f3ead7")
    ax.set_xlim(date(all_rows[0][0].year, 1, 1), date(all_rows[-1][0].year, 12, 31))
    ax.axvline(date(2022, 11, 30), color=GOLD, lw=2, ls=(0, (6, 4)))
    ax.annotate(
        "ChatGPT\n30. nov. 2022",
        (date(2022, 11, 30), 15.5),
        xytext=(8, 0),
        textcoords="offset points",
        color=GOLD,
        fontsize=18,
        va="top",
    )
    xs, ys = [r[0] for r in rows], [r[2] for r in rows]
    ax.plot(xs, ys, color=INK, lw=1.5, alpha=0.35)
    for d, k, h in rows:
        beyond = (
            h > 16
        )  # METR: estimates above 16 hours are not reliable with its task suite
        ax.scatter(
            d, h, s=90, color="white" if beyond else RED, edgecolor=RED, lw=2, zorder=3
        )
        if k in LABELS:
            ax.annotate(
                LABELS[k],
                (d, h),
                xytext=(-10, 8),
                textcoords="offset points",
                ha="right",
                fontsize=17,
            )
    ax.set_ylabel("Timer (for et menneske)", fontsize=18)
    ax.set_ylim(0, 18.5)
    ax.set_yticks([0, 4, 8, 12, 16])
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=INK, alpha=0.12)
    fig.tight_layout()
    fig.savefig(OUT / name, facecolor="#f3ead7")  # opaque: the stages are stacked


def imagenet_chart() -> None:
    # ILSVRC classification winners, top-5 error (%); human estimate from Russakovsky et al. 2015
    years = [2010, 2011, 2012, 2013, 2014, 2015]
    err = [28.2, 25.8, 15.3, 11.7, 6.7, 3.6]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.bar(years, err, width=0.6, color=[INK if y < 2012 else RED for y in years])
    ax.axhline(5.1, color=GOLD, lw=2, ls=(0, (6, 4)))
    ax.text(2015.5, 5.1, "Menneske\n(ca. 5 %)", color=GOLD, fontsize=18, va="center")
    ax.annotate(
        "Nevralt nett\n(AlexNet)",
        (2012, 15.3),
        xytext=(0, 12),
        textcoords="offset points",
        ha="center",
        fontsize=18,
        color=RED,
    )
    ax.set_ylabel("Feilrate (%)", fontsize=18)
    ax.set_xticks(years)
    ax.set_xlim(2009.5, 2015.4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=INK, alpha=0.12)
    ax.set_axisbelow(True)
    fig.savefig(OUT / "imagenet.svg", transparent=True, bbox_inches="tight")


def option_chart() -> None:
    import numpy as np
    from scipy.stats import norm

    k, t, r, sig = 100, 1.0, 0.03, 0.25
    s = np.linspace(50, 150, 400)
    d1 = (np.log(s / k) + (r + sig**2 / 2) * t) / (sig * np.sqrt(t))
    value = s * norm.cdf(d1) - k * np.exp(-r * t) * norm.cdf(d1 - sig * np.sqrt(t))
    fig, ax = plt.subplots(figsize=(7, 5.6))
    ax.plot(s, np.maximum(s - k, 0), color=INK, lw=3)
    ax.plot(s, value, color=GOLD, lw=3)
    price = value[np.argmin(abs(s - k))]
    ax.scatter([k], [price], s=90, color=RED, zorder=3)
    ax.annotate(
        "Pris i dag",
        (k, price),
        xytext=(-16, 18),
        textcoords="offset points",
        ha="right",
        color=RED,
        fontsize=19,
    )
    ax.text(124, 4, "Utbetaling\nved forfall", fontsize=18)
    ax.text(62, 9, "Verdi i dag", color=GOLD, fontsize=18)
    ax.set_xlabel("Aksjekurs", fontsize=18)
    ax.set_ylabel("Kroner", fontsize=18)
    ax.set_xticks([50, 100, 150])
    ax.set_yticks([0, 25, 50])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.savefig(OUT / "option.svg", transparent=True, bbox_inches="tight")


def pnl_chart() -> None:
    import numpy as np
    from scipy.stats import norm

    x = np.linspace(-4, 4, 400)
    var = norm.ppf(0.01)
    fig, ax = plt.subplots(figsize=(7, 5.6))
    ax.plot(x, norm.pdf(x), color=INK, lw=3)
    tail = x <= var
    ax.fill_between(x[tail], norm.pdf(x[tail]), color=RED, alpha=0.85)
    ax.axvline(var, color=RED, lw=2, ls=(0, (6, 4)))
    ax.text(
        var - 0.15,
        0.3,
        "VaR 99 %\n1 av 100 dager\ner verre",
        fontsize=18,
        color=RED,
        ha="right",
        va="top",
    )
    ax.set_xlim(-5.6, 4)
    ax.set_xlabel("Gevinst / tap i morgen", fontsize=18)
    ax.set_xticks([-3, 0, 3], ["Tap", "0", "Gevinst"])
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.savefig(OUT / "pnl.svg", transparent=True, bbox_inches="tight")


def kpi_fan(p: int = 3, horizon_end: str = "2030-12", n_paths: int = 4000) -> None:
    """Bayesian AR(p) on the 12-month KPI-JAE rate, with a fan of 60 intervals to 2030. For illustration."""
    import numpy as np
    import pandas as pd

    raw = pd.read_excel(
        Path.home() / "work/how-to-train-your-ai/data/forTecDay.xlsx"
    ).set_index("Time")
    level = raw["MSA_PCPIJAE"]
    level.index = pd.PeriodIndex([t.replace("M", "-") for t in level.index], freq="M")
    yoy = (100 * (level / level.shift(12) - 1)).loc["2001-01":].dropna()

    # Conjugate normal-inverse-gamma prior: lags shrunk towards zero, intercept loose
    X = np.column_stack(
        [np.ones(len(yoy) - p)] + [yoy.values[p - k - 1 : -k - 1] for k in range(p)]
    )
    yv = yoy.values[p:]
    V = np.linalg.inv(X.T @ X + np.diag([1e-4] + [1 / 0.5**2] * p))
    m = V @ X.T @ yv
    a = 2 + len(yv) / 2
    b = 0.1 + 0.5 * (yv @ yv - m @ np.linalg.inv(V) @ m)

    rng = np.random.default_rng(0)
    steps = (pd.Period(horizon_end, "M") - yoy.index[-1]).n
    paths = np.empty((n_paths, steps))
    for i in range(n_paths):
        sig2 = b / rng.gamma(a)
        beta = rng.multivariate_normal(m, sig2 * V)
        hist = list(yoy.values[-p:])
        for h in range(steps):
            hist.append(
                beta[0]
                + beta[1:] @ np.array(hist[-p:][::-1])
                + rng.normal(0, sig2**0.5)
            )
            paths[i, h] = hist[-1]
    # Start the fan at the last observation so it connects to the history
    fidx = pd.period_range(yoy.index[-1], periods=steps + 1, freq="M").to_timestamp()
    paths = np.column_stack([np.full(n_paths, yoy.iloc[-1]), paths])

    shown = yoy.loc["2015":]
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.axhline(2, color=GOLD, lw=2, ls=(0, (6, 4)))
    ax.text(date(2015, 4, 1), 1.85, "Mål: 2 %", color=GOLD, fontsize=18, va="top")
    for lvl in np.linspace(0.015, 0.95, 60):  # 60 nested intervals give a smooth fan
        lo, hi = np.percentile(paths, [50 - lvl * 50, 50 + lvl * 50], axis=0)
        ax.fill_between(fidx, lo, hi, color=RED, alpha=0.03, lw=0)
    ax.plot(fidx, np.median(paths, axis=0), color=RED, lw=2, ls=(0, (6, 4)))
    ax.plot(shown.index.to_timestamp(), shown.values, color=INK, lw=2.5)
    ax.set_ylabel("KPI-JAE, 12-mnd. endring (%)", fontsize=17)
    ax.set_ylim(-1, 8)
    ax.set_xlim(date(2015, 1, 1), date(2031, 1, 1))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=INK, alpha=0.12)
    fig.savefig(OUT / "kpi_fan.svg", transparent=True, bbox_inches="tight")


HALLEY = [
    1000,
    855,
    798,
    760,
    732,
    710,
    692,
    680,
    670,
    661,
    653,
    646,
    640,
    634,
    628,
    622,
    616,
    610,
    604,
    598,
    592,
    586,
    579,
    573,
    567,
    560,
    553,
    546,
    539,
    531,
    523,
    515,
    507,
    499,
    490,
    481,
    472,
    463,
    454,
    445,
    436,
    427,
    417,
    407,
    397,
    387,
    377,
    367,
    357,
    346,
    335,
    324,
    313,
    302,
    292,
    282,
    272,
    262,
    252,
    242,
    232,
    222,
    212,
    202,
    192,
    182,
    172,
    162,
    152,
    142,
    131,
    120,
    109,
    98,
    88,
    78,
    68,
    58,
    49,
    41,
    34,
    28,
    23,
    20,
]  # persons living at age 1..84 per 1000 (Halley 1693)


def halley_bins() -> None:
    """Small panels for the four-steps slide: a binned mortality model, empty (parameters) and fitted to Halley."""
    import numpy as np

    lx = np.array(HALLEY, dtype=float)
    ages = np.arange(1, 84)
    qx = 1 - lx[1:] / lx[:-1]  # yearly probability of dying at age 1..83
    edges = [3, 13, 23, 33, 43, 53, 63, 73, 84]
    theta = [qx[(ages >= a) & (ages < b)].mean() for a, b in itertools.pairwise(edges)]
    mids = [(a + b) / 2 for a, b in itertools.pairwise(edges)]
    widths = [b - a - 1.2 for a, b in itertools.pairwise(edges)]
    for name, fitted in [("fs_model.svg", False), ("fs_train.svg", True)]:
        fig, ax = plt.subplots(figsize=(4.2, 3.4))
        if fitted:
            ax.bar(mids, theta, width=widths, color=GOLD, alpha=0.9)
            sel = ages >= 3
            ax.scatter(ages[sel], qx[sel], s=12, color=INK, zorder=3)
        else:
            # untrained model: a guessed level per bin, with wide uncertainty
            guess = np.array([0.02, 0.02, 0.025, 0.03, 0.04, 0.06, 0.09, 0.12])
            lo, hi = guess * 0.3, np.minimum(guess * 2.2, 0.19)
            ax.bar(mids, hi - lo, bottom=lo, width=widths, color=GOLD, alpha=0.18)
            ax.bar(mids, guess, width=widths, color=GOLD, alpha=0.45)
            ax.errorbar(
                mids,
                guess,
                yerr=[guess - lo, hi - guess],
                fmt="none",
                ecolor=INK,
                elinewidth=1.5,
                capsize=4,
            )
        ax.set_ylim(0, 0.2)
        ax.set_yticks([])
        ax.set_xticks([3, 43, 83])
        ax.set_xlabel("alder", fontsize=16)
        ax.tick_params(labelsize=14)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        fig.savefig(OUT / name, transparent=True, bbox_inches="tight")
    print("theta per bin:", [round(t, 3) for t in theta])


metr_chart(date(2022, 11, 29), "metr_1.svg")
metr_chart(date(2025, 8, 7), "metr_2.svg")
metr_chart(date(2100, 1, 1), "metr_3.svg")
imagenet_chart()
option_chart()
pnl_chart()
kpi_fan()
halley_bins()
