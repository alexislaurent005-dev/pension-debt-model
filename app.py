"""Interactive front end for the pension / debt-to-GDP model.

All the economics lives in src/ (written by Alexis). This file only builds
the controls and charts, and calls debt_projection() and
generate_random_paths() with whatever the reader chooses.
"""
import random

import altair as alt
import pandas as pd
import streamlit as st

from src import params
from src.montecarlo import generate_random_paths
from src.simulation import debt_projection

N_YEARS = params.FINAL_YEAR - params.FIRST_YEAR + 1
REPO_URL = "https://github.com/alexislaurent005-dev/pension-debt-model"

SCENARIO_COLOUR = "#1B7F79"   # teal: the reader's scenario
BASELINE_COLOUR = "#B23A48"   # muted red: the current triple lock

RULES = {
    "Triple lock (current policy)": "triple_lock",
    "Smoothed earnings link (Burnham reform, our reading)": "smoothed_earnings",
    "Double lock: inflation or floor": "double_lock",
    "Earnings only": "earnings",
    "Inflation (CPI) only": "cpi",
}

# Presets set every control at once. Values are stored in session_state
# under the same keys the widgets use.
DEFAULTS = {
    "rule": "Triple lock (current policy)",
    "reform_year": 2030,
    "floor": params.TRIPLE_LOCK_FLOOR * 100,
    "means_test": False,
    "threshold": float(params.MEANS_TEST_THRESHOLD),
    "taper": params.TAPER_RATE * 100,
    "threshold_link": "Pension uprating",
    "real_growth": params.REAL_GDP_GROWTH * 100,
    "inflation": params.INFLATION_RATE * 100,
    "productivity": params.PRODUCTIVITY_GROWTH * 100,
    "gilt": params.GILT_RATE * 100,
    "pensioner_growth": params.PENSIONER_GROWTH * 100,
    "start_debt": params.STARTING_DEBT_TO_GDP * 100,
    "uncertainty": True,
    "runs": 1000,
    "sd_inflation": params.INFLATION_STD_DEV * 100,
    "sd_productivity": params.PRODUCTIVITY_STD_DEV * 100,
}
PRESETS = {
    "Current policy": {},
    "Burnham reform from 2030": {"rule": "Smoothed earnings link (Burnham reform, our reading)"},
    "Burnham reform + means test": {"rule": "Smoothed earnings link (Burnham reform, our reading)",
                                    "means_test": True},
}


def apply_preset():
    choice = st.session_state["preset"]
    for key, value in {**DEFAULTS, **PRESETS[choice]}.items():
        st.session_state[key] = value


# ---------------------------------------------------------------- model calls
def projection_settings(s, scenario=True):
    """Translate control values into debt_projection() keyword arguments."""
    common = dict(
        debt_to_gdp=s["start_debt"] / 100,
        r_gdp=s["real_growth"] / 100,
        gilt_rate=s["gilt"] / 100,
        pensioner_growth=s["pensioner_growth"] / 100,
    )
    if not scenario:  # the comparison line: today's universal triple lock, 2.5% floor
        return {**common, "taper_rate": 0}
    rule = RULES[s["rule"]]
    return {
        **common,
        "tlock_floor": s["floor"] / 100,
        "uprating_rule": rule,
        "reform_year": None if rule == "triple_lock" else s["reform_year"],
        "taper_rate": s["taper"] / 100 if s["means_test"] else 0,
        "threshold": s["threshold"],
        "threshold_uprating": "earnings" if s["threshold_link"] == "Earnings" else "pension",
    }


@st.cache_data(show_spinner=False)
def run_deterministic(settings_items):
    s = dict(settings_items)
    inflation = [s["inflation"] / 100] * N_YEARS
    productivity = [s["productivity"] / 100] * N_YEARS
    out = {}
    for name, scenario in [("scenario", True), ("baseline", False)]:
        years, shares, debts = debt_projection(inflation=inflation, productivity_growth=productivity,
                                               **projection_settings(s, scenario))
        out[name] = {"years": years, "debt": debts, "pension": shares}
    return out


@st.cache_data(show_spinner=False)
def run_uncertain(settings_items):
    s = dict(settings_items)
    random.seed(42)
    inflation_paths, productivity_paths = generate_random_paths(
        params.FIRST_YEAR, params.FINAL_YEAR, s["runs"], s["inflation"] / 100, s["productivity"] / 100,
        s["sd_inflation"] / 100, s["sd_productivity"] / 100)
    out = {}
    for name, scenario in [("scenario", True), ("baseline", False)]:
        debt_runs, pension_runs = [], []
        for i in range(s["runs"]):
            years, shares, debts = debt_projection(inflation=inflation_paths[i],
                                                   productivity_growth=productivity_paths[i],
                                                   **projection_settings(s, scenario))
            debt_runs.append(debts)
            pension_runs.append(shares)
        out[name] = {"years": years, "debt": percentiles_by_year(debt_runs),
                     "pension": percentiles_by_year(pension_runs)}
    return out


def percentiles_by_year(runs):
    """5th, 50th and 95th percentile across runs, year by year."""
    n = len(runs)
    result = {"p5": [], "p50": [], "p95": []}
    for t in range(len(runs[0])):
        column = sorted(run[t] for run in runs)
        result["p5"].append(column[int(0.05 * n)])
        result["p50"].append(column[int(0.50 * n)])
        result["p95"].append(column[int(0.95 * n)])
    return result


# ---------------------------------------------------------------- charts
def chart(results, measure, title, uncertain):
    rows = []
    for name, label in [("baseline", "Triple lock (current policy)"), ("scenario", "Your scenario")]:
        series = results[name][measure]
        for t, year in enumerate(results[name]["years"]):
            if uncertain:
                rows.append({"Year": year, "Policy": label, "Central": series["p50"][t] * 100,
                             "Low": series["p5"][t] * 100, "High": series["p95"][t] * 100})
            else:
                rows.append({"Year": year, "Policy": label, "Central": series[t] * 100})
    df = pd.DataFrame(rows)
    colour_scale = alt.Scale(domain=["Triple lock (current policy)", "Your scenario"],
                             range=[BASELINE_COLOUR, SCENARIO_COLOUR])
    colour = alt.Color("Policy:N", scale=colour_scale,
                       legend=alt.Legend(orient="top", title=None))
    x = alt.X("Year:Q", axis=alt.Axis(format="d", title=None, tickCount=6),
              scale=alt.Scale(domain=[params.FIRST_YEAR, params.FINAL_YEAR], nice=False))
    y_title = f"{title}, % of GDP"
    dash = alt.StrokeDash("Policy:N", scale=alt.Scale(
        domain=["Triple lock (current policy)", "Your scenario"], range=[[6, 4], [1, 0]]),
        legend=alt.Legend(orient="top", title=None))
    lines = alt.Chart(df).mark_line(strokeWidth=2.5).encode(
        x=x, y=alt.Y("Central:Q", title=y_title), color=colour, strokeDash=dash,
        tooltip=[alt.Tooltip("Year:Q", format="d"), "Policy:N",
                 alt.Tooltip("Central:Q", title="% of GDP", format=".1f")])
    if not uncertain:
        return lines.properties(height=360)
    band = alt.Chart(df).mark_area(opacity=0.14).encode(
        x=x, y=alt.Y("Low:Q", title=y_title), y2="High:Q",
        color=colour)
    return (band + lines).properties(height=360)


# ---------------------------------------------------------------- page
st.set_page_config(page_title="Pension policy and UK debt, 2026-2076", layout="wide")
st.markdown("""
<style>
h1, h2, h3, [data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {
  font-family: Georgia, "Times New Roman", serif !important; font-weight: 600 !important; letter-spacing: -0.01em; }
[data-testid="stMarkdownContainer"] p.readout { font-family: Georgia, serif; font-size: 1.5rem !important;
  line-height: 1.45 !important; max-width: 60rem; margin: 0.2rem 0 1.2rem 0; }
.readout b.scen { color: #1B7F79; }
.readout b.base { color: #B23A48; }
.small-note { color: #5A6472; font-size: 0.9rem; max-width: 62rem; }
</style>""", unsafe_allow_html=True)

if "rule" not in st.session_state:
    # First visit: open on the question readers are most likely to have.
    st.session_state["preset"] = "Burnham reform from 2030"
    apply_preset()

with st.sidebar:
    st.selectbox("Start from", list(PRESETS), key="preset", on_change=apply_preset)

    st.subheader("Pension uprating")
    st.selectbox("Rule", list(RULES), key="rule",
                 help="How the State Pension rises each year. Reforms apply from the chosen year; "
                      "the triple lock applies before it.")
    reform_on = RULES[st.session_state["rule"]] != "triple_lock"
    st.slider("Reform starts in", 2027, 2060, key="reform_year", disabled=not reform_on)
    st.slider("Floor (%)", 0.0, 5.0, step=0.1, key="floor",
              help="Minimum annual rise under the triple and double locks. Currently 2.5%.")

    st.subheader("Means test")
    st.toggle("Means-test the State Pension", key="means_test",
              help="Withdraw pension gradually from pensioners with private income above a threshold.")
    mt_on = st.session_state["means_test"]
    st.slider("Threshold (£ per week of other income)", 0.0, 600.0, step=5.0, key="threshold", disabled=not mt_on)
    st.slider("Taper (pence withdrawn per £1 above it)", 0.0, 100.0, step=1.0, key="taper", disabled=not mt_on)
    st.radio("Threshold rises with", ["Pension uprating", "Earnings"], key="threshold_link",
             horizontal=True, disabled=not mt_on)

    st.subheader("Economy")
    st.slider("Real GDP growth (%)", 0.0, 3.0, step=0.1, key="real_growth")
    st.slider("Inflation (%)", 0.0, 6.0, step=0.1, key="inflation")
    st.slider("Real earnings growth (%)", -1.0, 3.0, step=0.1, key="productivity")
    st.slider("Interest rate on debt (%)", 0.0, 8.0, step=0.1, key="gilt")
    st.slider("Pensioner population growth (%)", 0.0, 2.0, step=0.05, key="pensioner_growth")
    st.slider("Debt today (% of GDP)", 50.0, 150.0, step=0.5, key="start_debt")

    st.subheader("Uncertainty")
    st.toggle("Simulate volatile inflation and earnings", key="uncertainty",
              help="Runs the model on many random economic futures (Monte Carlo) and shows the "
                   "middle 90% of outcomes. Volatility is calibrated on 2011-2026 UK data.")
    unc_on = st.session_state["uncertainty"]
    st.select_slider("Simulated futures", [100, 250, 500, 1000], key="runs", disabled=not unc_on)
    st.slider("Inflation volatility (pp)", 0.0, 4.0, step=0.05, key="sd_inflation", disabled=not unc_on)
    st.slider("Real earnings volatility (pp)", 0.0, 4.0, step=0.05, key="sd_productivity", disabled=not unc_on)

settings = {key: st.session_state[key] for key in DEFAULTS}
settings_items = tuple(sorted(settings.items()))
uncertain = settings["uncertainty"]
with st.spinner("Running the model"):
    results = run_uncertain(settings_items) if uncertain else run_deterministic(settings_items)

st.title("Pension uprating and UK public debt, 2026-2076")


def final(name, measure, key="p50"):
    series = results[name][measure]
    return (series[key][-1] if uncertain else series[-1]) * 100


scen, base = final("scenario", "debt"), final("baseline", "debt")
gap = base - scen
if abs(gap) < 0.5:
    comparison = "about the same as keeping the triple lock"
elif gap > 0:
    comparison = f"{gap:.0f} points lower than keeping the triple lock (<b class='base'>{base:.0f}%</b>)"
else:
    comparison = f"{-gap:.0f} points higher than keeping the triple lock (<b class='base'>{base:.0f}%</b>)"
lead = "In the median simulated future, public" if uncertain else "Public"
if scen >= 0:
    outcome = f"debt reaches <b class='scen'>{scen:.0f}% of GDP</b>"
else:
    outcome = f"debt is paid off entirely, leaving <b class='scen'>net assets of {-scen:.0f}% of GDP</b>"
sentence = f"{lead} {outcome} in 2076 under your settings, {comparison}."
if uncertain:
    lo, hi = final("scenario", "debt", "p5"), final("scenario", "debt", "p95")
    sentence += f" In 90% of futures it lands between {lo:.0f}% and {hi:.0f}%."
st.markdown(f"<p class='readout'>{sentence}</p>", unsafe_allow_html=True)
if not uncertain and RULES[settings["rule"]] in ("smoothed_earnings", "earnings"):
    st.info("With steady inflation and earnings, earnings always beat inflation, so this reform behaves just "
            "like the triple lock. Its effect comes from removing the triple lock's ratchet in volatile years: "
            "switch on **Simulate volatile inflation and earnings** in the sidebar to see it.")

st.altair_chart(chart(results, "debt", "Public debt", uncertain), width="stretch")
if uncertain:
    st.markdown(f"<p class='small-note'>Lines show the median of {settings['runs']:,} simulated futures; "
                "shading covers the middle 90%. The dashed red line keeps today's triple lock in the same futures.</p>",
                unsafe_allow_html=True)

pen_s, pen_b = final("scenario", "pension"), final("baseline", "pension")
st.subheader("State Pension spending")
st.markdown(f"<p class='small-note'>{pen_s:.1f}% of GDP in 2076 under your settings, against "
            f"{pen_b:.1f}% under the triple lock. A lower line means pensions grow more slowly "
            f"than the economy, so the saving comes from pensioners' relative incomes.</p>",
            unsafe_allow_html=True)
st.altair_chart(chart(results, "pension", "Spending", uncertain), width="stretch")

with st.expander("How the model works"):
    st.markdown(f"""
Each year the model grows State Pension spending by the uprating rule and the number of pensioners,
relative to the size of the economy, then updates debt with the standard identity:
debt grows with the interest rate, shrinks relative to GDP as the economy grows, and moves
with any change in pension spending compared with today (all other spending and tax is held
at today's share of GDP). This isolates the effect of pension policy; it is not a full fiscal forecast.

**Means test.** Pensioners keep the full pension (£{params.MAX_PENSION:.2f} a week) until their other
income passes the threshold, then lose the taper rate for every £1 above it. Pensioner incomes come
from DWP's *Pensioners' Incomes* series, in ten bands for singles and couples, weighted by population.

**Burnham reform.** In September 2026 the Prime Minister announced the triple lock will be kept until
April 2030, then replaced by a double lock (inflation or 2.5%) with a longer-term adjustment to keep
pace with earnings. The details are unpublished; the "smoothed earnings link" option is our reading:
a double lock each year, with catch-up whenever the pension falls behind an earnings-linked path.

**Uncertainty.** With volatility switched on, inflation and real earnings are drawn at random each year
around the chosen averages, with spreads calibrated on the triple lock's own inputs from 2011/12 to
2026/27. Because the triple lock keeps the highest of its measures and never gives it back, volatility
raises its cost. Treat the ranges as a stress test rather than a forecast.

Code, data sources, findings and limitations: [{REPO_URL}]({REPO_URL})
""")
st.markdown("<p class='small-note'>Model and analysis by Alexis Laurent, BSc Economics and International "
            "Development, University of Sussex.</p>", unsafe_allow_html=True)
