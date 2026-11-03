import io

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import RidgeCV


def ssb_wide(table: str, sel: dict, key: str) -> pd.DataFrame:
    q = "&".join(f"valueCodes[{k}]={v}" for k, v in sel.items())
    url = f"https://data.ssb.no/api/pxwebapi/v2/tables/{table}/data?lang=en&outputformat=csv&outputFormatParams=UseCodes&{q}"
    df = pd.read_csv(io.StringIO(requests.get(url).text), na_values=".")
    df = df.set_index(key).filter(regex=r"\d{4}M\d{2}").T
    df.index = pd.PeriodIndex(
        [c.split()[-1].replace("M", "-") for c in df.index], freq="M"
    )
    return df


tot = ssb_wide(
    "14706",
    {"KPIavledetSerie": "KPI-JAE", "ContentsCode": "KPIJustIndMnd", "Tid": "*"},
    "KPIavledetSerie",
)["KPI-JAE"]
grp = ssb_wide(
    "14704",
    {
        "KPIavledetSerie": "KPI-JAE",
        "VareTjenesteGrp": "*",
        "ContentsCode": "KPIJustIndMnd",
        "Tid": "*",
    },
    "VareTjenesteGrp",
)
fx = pd.read_csv(
    "https://data.norges-bank.no/api/data/EXR/M.I44.NOK.SP?format=csv&startPeriod=1995-01&locale=en",
    sep=";",
)
fx = fx.set_index(pd.PeriodIndex(fx.TIME_PERIOD, freq="M")).OBS_VALUE.rename("I44")

d = pd.DataFrame({"jae": tot}).join(grp.add_prefix("g"), how="left").join(fx)
d.to_csv("dataset.csv")
mm = np.log(d).diff() * 100  # monthly log change, percent
yoy = (np.log(d.jae).diff(12) * 100).rename("yoy")
print(d.dropna().index.min(), d.index.max(), d.shape)

# target: KPI-JAE yoy next month. Info at t: everything up to and including month t.
X = pd.DataFrame(index=d.index)
for k in range(12):
    X[f"jae_l{k}"] = mm.jae.shift(k)
for c in [c for c in mm if c.startswith("g") and c != "g0"]:
    X[f"{c}_l0"] = mm[c]
X["fx_l0"], X["fx_3m"] = mm.I44, mm.I44.rolling(3).sum()
X["yoy"] = yoy
X["month"] = d.index.month
X = X.join(pd.get_dummies(d.index.month, prefix="m").set_index(d.index).astype(float))
y_mm = mm.jae.shift(-1)
y = yoy.shift(-1)
base = yoy - mm.jae.shift(11)  # yoy next = base + next m/m
df = X.join(y.rename("y")).join(y_mm.rename("y_mm")).join(base.rename("base")).dropna()

preds = {
    "naiv: samme som forrige mnd": [],
    "sesongsnitt (siste 5 år)": [],
    "ridge": [],
    "gbm": [],
}
truth, idx = [], []
for t in df.index[df.index >= pd.Period("2015-01", "M")]:
    tr = df[
        df.index < t - 0
    ]  # rows whose target is known before forecasting at t (target is t+1, so train < t)
    tr = tr[tr.index < t]
    row = df.loc[[t]]
    feats = [c for c in df if c not in ("y", "y_mm", "base", "month")]
    same_month = (
        mm.jae[(mm.index < t + 1) & (mm.index.month == (t + 1).month)].tail(5).mean()
    )
    preds["naiv: samme som forrige mnd"].append(row.yoy.item())
    preds["sesongsnitt (siste 5 år)"].append(row.base.item() + same_month)
    r = RidgeCV(alphas=np.logspace(-2, 3, 20)).fit(tr[feats], tr.y_mm)
    preds["ridge"].append(row.base.item() + r.predict(row[feats])[0])
    g = GradientBoostingRegressor(
        n_estimators=200, max_depth=2, learning_rate=0.05, subsample=0.8, random_state=0
    ).fit(tr[feats], tr.y_mm)
    preds["gbm"].append(row.base.item() + g.predict(row[feats])[0])
    truth.append(row.y.item())
    idx.append(t + 1)
truth = np.array(truth)
for k, v in preds.items():
    e = np.array(v) - truth
    print(
        f"{k:32s} RMSE {np.sqrt((e**2).mean()):.3f}  MAE {np.abs(e).mean():.3f}  (n={len(e)})"
    )
pd.DataFrame(preds, index=idx).assign(fasit=truth).to_csv("preds.csv")
