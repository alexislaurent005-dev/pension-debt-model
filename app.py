"""Interactive front end for the pension / debt-to-GDP model.

All the economics lives in src/ (written by Alexis). This file only builds
the controls and charts, and calls debt_projection() and
generate_random_paths() with whatever the reader chooses.

Layout: one screen, no scrolling. The chart sits in the centre, with the
controls around it (pension policy on the left, the economy on the right,
the view and uncertainty along the bottom). Everything written, the
explanation, findings and limitations, lives in a panel that slides out
from the right when the reader asks for it.
"""
import random
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src import params
from src.montecarlo import generate_random_paths
from src.simulation import debt_projection

N_YEARS = params.FINAL_YEAR - params.FIRST_YEAR + 1
# Nominal GDP 2026-27, OBR Economic and fiscal outlook, November 2025 (£bn). Used only to
# translate shares of GDP into pounds at today's size of the economy.
GDP_2026_27_BN = 3165
REPO_URL = "https://github.com/alexislaurent005-dev/pension-debt-model"
README_PDF = Path(__file__).parent / "docs" / "README.pdf"

SCENARIO_COLOUR = "#1B7F79"   # teal: the reader's scenario
BASELINE_COLOUR = "#B23A48"   # muted red: the current triple lock

RULES = {
    "Triple lock (current policy)": "triple_lock",
    "Burnham reform (smoothed earnings link)": "smoothed_earnings",
    "Double lock: inflation or floor": "double_lock",
    "Earnings only": "earnings",
    "Inflation (CPI) only": "cpi",
}

# What the chart in the centre shows. The reader switches between these along the bottom.
VIEWS = ["Public debt", "Pension spending", "Saving needed"]

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
    "debt_target": 100.0,
}
PRESETS = {
    "Current policy": {},
    "Burnham reform from 2030": {"rule": "Burnham reform (smoothed earnings link)"},
    "Burnham reform + means test": {"rule": "Burnham reform (smoothed earnings link)",
                                    "means_test": True},
    "Hold debt at 100% of GDP": {"rule": "Burnham reform (smoothed earnings link)",
                                 "view": "Saving needed"},
}


def apply_preset():
    choice = st.session_state["preset"]
    preset = dict(PRESETS[choice])
    st.session_state["view"] = preset.pop("view", "Public debt")
    for key, value in {**DEFAULTS, **preset}.items():
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


def saving_to_hold_target(pension_shares, inflation_path, s):
    """Extra saving (% of GDP, as a fraction) needed each year to stop debt rising above the target.

    Rebuilds the debt path with the same identity as debt_projection(), using that run's
    pension spending, and whenever debt would end the year above the target, records the
    primary surplus needed to hold it there. Without a target this reproduces debt_projection()
    exactly (checked in testing).
    """
    target = s["debt_target"] / 100
    debt = s["start_debt"] / 100
    savings = []
    for t in range(N_YEARS):
        nominal_growth = s["real_growth"] / 100 + inflation_path[t]
        next_debt = (debt * (1 + s["gilt"] / 100) / (1 + nominal_growth)
                     - (params.PENSION_EXPENDITURE - pension_shares[t]))
        needed = max(0.0, next_debt - target)
        savings.append(needed)
        debt = next_debt - needed
    return savings


@st.cache_data(show_spinner=False)
def run_deterministic(settings_items):
    s = dict(settings_items)
    inflation = [s["inflation"] / 100] * N_YEARS
    productivity = [s["productivity"] / 100] * N_YEARS
    out = {}
    for name, scenario in [("scenario", True), ("baseline", False)]:
        years, shares, debts = debt_projection(inflation=inflation, productivity_growth=productivity,
                                               **projection_settings(s, scenario))
        out[name] = {"years": years, "debt": debts, "pension": shares,
                     "saving": saving_to_hold_target(shares, inflation, s)}
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
        debt_runs, pension_runs, saving_runs = [], [], []
        for i in range(s["runs"]):
            years, shares, debts = debt_projection(inflation=inflation_paths[i],
                                                   productivity_growth=productivity_paths[i],
                                                   **projection_settings(s, scenario))
            debt_runs.append(debts)
            pension_runs.append(shares)
            saving_runs.append(saving_to_hold_target(shares, inflation_paths[i], s))
        out[name] = {"years": years, "debt": percentiles_by_year(debt_runs),
                     "pension": percentiles_by_year(pension_runs),
                     "saving": percentiles_by_year(saving_runs)}
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
def chart(results, measure, title, uncertain, note=""):
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
    legend = alt.Legend(orient="top-left", title=None, labelLimit=400, labelFontSize=14, symbolType="stroke",
                        symbolStrokeWidth=2.5, symbolSize=300,
                        fillColor="rgba(255,255,255,0.85)", padding=6)
    colour = alt.Color("Policy:N", scale=colour_scale, legend=legend)
    band_colour = alt.Color("Policy:N", scale=colour_scale, legend=None)
    x = alt.X("Year:Q", axis=alt.Axis(format="d", title=None, tickCount=6),
              scale=alt.Scale(domain=[params.FIRST_YEAR, params.FINAL_YEAR], nice=False))
    y_title = f"{title}, % of GDP"
    dash = alt.StrokeDash("Policy:N", scale=alt.Scale(
        domain=["Triple lock (current policy)", "Your scenario"], range=[[6, 4], [1, 0]]),
        legend=None)
    lines = alt.Chart(df).mark_line(strokeWidth=2.5).encode(
        x=x, y=alt.Y("Central:Q", title=y_title, axis=alt.Axis(tickCount=8)), color=colour, strokeDash=dash,
        tooltip=[alt.Tooltip("Year:Q", format="d"), "Policy:N",
                 alt.Tooltip("Central:Q", title="% of GDP", format=".1f")])
    layers = lines
    if uncertain:
        band = alt.Chart(df).mark_area(opacity=0.14).encode(
            x=x, y=alt.Y("Low:Q", title=y_title), y2="High:Q", color=band_colour)
        layers = (band + lines).resolve_legend(color="independent")
    return layers.properties(
        height="container", width="container",
        title=alt.TitleParams(note, anchor="end", orient="bottom", fontSize=12, font="Georgia",
                              fontWeight="normal", color="#5A6472", offset=6),
    ).configure_view(strokeWidth=0).configure_axis(
        labelFontSize=13, titleFontSize=14, labelFont="Georgia", titleFont="Georgia",
        titleFontWeight="normal").configure_legend(labelFont="Georgia")


# ---------------------------------------------------------------- the slide-out panel
@st.dialog("The story behind the model", width="medium", position="right")
def story_panel():
    st.markdown(
        "A Python model projecting how the design of the UK State Pension affects the long-run "
        "path of UK public debt, from 2026 to 2076. Everything below is a shorter version of "
        "the full write-up.")
    if README_PDF.exists():
        st.download_button("Download the full write-up (PDF)", README_PDF.read_bytes(),
                           file_name="Pension-debt-model-Alexis-Laurent.pdf", mime="application/pdf",
                           icon=":material/download:", type="primary", key="pdf_panel")

    idea, ratchet, found, built, limits, words = st.tabs(
        ["The question", "The ratchet", "What I found", "How it works", "Limits", "Key terms"])

    with idea:
        st.markdown("""
#### How do the State Pension's rules shape UK debt?

With ever-tightening fiscal headroom, finding ways to reduce government spending matters more and
more. In an Advanced Macroeconomics group project on cutting UK debt-to-GDP, I wanted a policy that
didn't rely on hopes of growth. So we looked at how the Treasury spends its money, and pensions, with
the triple lock, stood out as a large and fast-rising cost.

We proposed a means-tested pension. The idea worked, but the model was crude: it cut the pension off
entirely above a threshold, a cliff edge that punished saving. This model is my attempt to do it
properly. It replaces the cliff edge with a gradual 55% taper, is calibrated on published OBR, ONS
and DWP data, simulates economic volatility, and lets you explore the scenarios yourself.

It compares three things: the **triple lock** as it is today, **my means-tested alternative**, and
the **uprating reform** announced by Prime Minister Andy Burnham in September 2026.
""")

    with ratchet:
        st.markdown("""
#### Why the triple lock costs more when the economy is bumpy

Each year, the triple lock raises the pension by the **highest** of inflation, earnings growth or 2.5%,
and every rise is kept. It picks up whichever rate is high that year, but never falls back when that
rate drops. That is a ratchet.

So its cost depends on how much inflation and earnings **move around**, not just on their averages.
(In economic terms, the maximum of several rates is a convex function, so its average is higher than
the maximum of their averages: Jensen's inequality.)

A simple test shows it. If inflation and earnings alternate between high and low years but keep the
same averages, the pension rises by about 3.9% a year instead of 3.6%, and 2076 debt reaches 206% of
GDP instead of 182%.

**Try it:** switch *Volatile economy* on and off under the chart.
""")

    with found:
        st.markdown("""
#### The headline results (median of 1,000 simulated futures, 2076)

| | Universal pension | Means-tested |
|---|---|---|
| Triple lock | 288% of GDP | 212% |
| Burnham reform (smoothed earnings link) from 2030 | 219% | **140%** |

- **Volatility matters most.** It raises median 2076 debt under the triple lock from 182% (steady
  rates) to 288%.
- **The reform's value is invisible under central assumptions.** With steady rates, Burnham's reform
  saves nothing. With volatility, it cuts median debt by 69 percentage points, because its whole
  effect is removing the ratchet.
- **Means testing cuts the level of spending** by about 22%, from 5% to 3.9% of GDP. About two-thirds
  of pensioners keep the full pension; the saving comes from the richest third.
- **The two policies are complements.** Means testing lowers spending; reform removes the ratchet.
  Together they take median debt from 288% to 140% of GDP.

These are stress tests under simplified assumptions, not forecasts.
""")

    with built:
        st.markdown(f"""
#### Debt
Each year, debt grows with the interest paid on it, shrinks relative to a growing economy, and changes
with the government's budget balance:
""")
        st.latex(r"b_t = \frac{1 + r}{1 + g_t}\, b_{t-1} - pb_t")
        st.markdown(f"""
All other spending and tax are held at today's share of GDP, so the debt paths show **only the
difference the pension makes**, not a full forecast. Debt starts at 93.8% of GDP (ONS, August 2026).
Because the interest rate (4.3%) is higher than nominal growth (3.7%), any extra spending compounds.

#### Pension spending
Spending grows with the uprating rule and the number of pensioners (0.85% a year), relative to the
economy:
""")
        st.latex(r"s_t = s_{t-1} \cdot \frac{(1 + u_t)(1 + n)}{1 + g_t}")
        st.markdown(f"""
#### Means test
Everyone gets the full pension (£{params.MAX_PENSION:.2f} a week) minus 55p for every £1 of other
income above £238 a week, Universal Credit's taper and the Pension Credit guarantee. Pensioner incomes
come from DWP *Pensioners' Incomes* (Table 4.4), in ten bands for singles and couples.

#### Burnham reform
The triple lock stays until 2030, then becomes a double lock (inflation or 2.5%) with an adjustment to
keep pace with earnings. The details are unpublished, so the *smoothed earnings link* is my reading:
a double lock, with catch-up whenever the pension falls behind an earnings-linked path.

#### Uncertainty
The *Volatile economy* switch runs 1,000 futures, each with its own random path of inflation and
earnings, with spreads calibrated on 2011/12 to 2026/27 data. Every policy faces the same futures,
so differences come from the policy, not from chance.

#### Saving needed
This view adds just enough extra saving (spending cuts or tax rises elsewhere) to stop debt rising
above the target, and shows how much that is each year.
""")

    with limits:
        st.markdown("""
#### What the model leaves out

- **Everything else is frozen.** Tax, other spending and the interest rate stay constant for 50 years.
  Gilts are already above 5.4% (October 2026); at that rate, triple lock debt reaches 280% of GDP by
  2076 rather than 182%.
- **Pensioner growth is fixed** at 0.85% a year, though an ageing population may push it higher, so the
  model may understate the triple lock's cost.
- **Each simulated year is independent**, whilst real shocks, like the 2022–24 inflation spike, last
  several years.
- **Nobody changes their behaviour.** A 55% taper acts like a tax on savings, so some may save less.
  Everyone is also assumed to claim, though real Pension Credit take-up is well below 100%.
- **No government would let debt reach 288% of GDP** without responding. Read the numbers as rough
  sizes, not predictions.
""")

    with words:
        st.markdown("""
| Term | Meaning |
|---|---|
| Debt-to-GDP | Government debt as a share of the size of the economy. 100% means debt equals one year of national output. |
| Uprating | The yearly increase in the State Pension. |
| Triple lock | The pension rises by the highest of inflation, average earnings growth, or 2.5%. |
| Means test | Reducing a benefit for people with higher incomes from other sources. |
| Percentage points | The gap between two percentages: 288% to 219% is 69 points. |
| Monte Carlo | Running the model many times, each with a different random economy. |
| Median | The middle outcome. The shading covers the middle 90%. |
""")

    st.markdown(f"<p class='small-note'>Code, data sources and full findings: "
                f"<a href='{REPO_URL}' target='_blank'>GitHub</a>. Model and analysis by Alexis Laurent, "
                "BA Economics and International Development, University of Sussex.</p>",
                unsafe_allow_html=True)


# ---------------------------------------------------------------- page
st.set_page_config(page_title="Pension policy and UK debt, 2026-2076", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], p, label, li, input, button, textarea {
  font-family: Georgia, "Times New Roman", serif !important; }
h1, h2, h3, h4 { font-family: Georgia, "Times New Roman", serif !important; font-weight: 600 !important;
  letter-spacing: -0.01em; }

/* one screen, full width: side margins, and room at the top for Streamlit's toolbar */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 100% !important; padding: 2.4rem 3.5rem 0.4rem 3.5rem !important; }
[data-testid="stVerticalBlock"] { gap: 0.45rem; }
[data-testid="stWidgetLabel"] p { font-size: 0.98rem !important; }
[data-baseweb="select"] div, [data-testid="stPopover"] button p, [data-testid="stBaseButton-segmented_control"] p,
[data-testid="stBaseButton-segmented_controlActive"] p { font-size: 0.98rem !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBar"] { font-size: 0.9rem; }

/* the chart fills whatever height the window leaves after the title and the controls */
[data-testid="stLayoutWrapper"]:has(> .st-key-chartbox), .st-key-chartbox {
  height: calc(100vh - 300px) !important; min-height: 330px; flex: 0 0 auto !important; }

/* the side panels stretch to the same height as the chart and spread their controls out */
[data-testid="stLayoutWrapper"]:has(> .st-key-leftpanel), .st-key-leftpanel {
  height: calc(100vh - 150px) !important; min-height: 500px; flex: 0 0 auto !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-rightpanel), .st-key-rightpanel {
  height: calc(100vh - 215px) !important; min-height: 430px; flex: 0 0 auto !important; }
.st-key-leftpanel, .st-key-rightpanel { justify-content: space-between; }
.st-key-chartbox [data-testid="stVegaLiteChart"], .st-key-chartbox .stVegaLiteChart { height: 100%; }

.page-head { text-align: center; padding: 0 1rem 0.6rem 1rem; }
h1.page-title { font-size: 2.05rem !important; margin: 0 !important; padding: 0 !important; line-height: 1.2; }
p.readout { font-size: 1.18rem !important; line-height: 1.5 !important; margin: 0.35rem auto 0 auto;
  max-width: 62rem; color: #1C2A2E; }
.readout b.scen { color: #1B7F79; }
.readout b.base { color: #B23A48; }
.readout b.num { color: #1C2A2E; }
.readout .aside { color: #5A6472; font-style: italic; }
.small-note { color: #5A6472; font-size: 0.9rem; margin: 0; }
.small-note a { color: #1B7F79; }
.footer { text-align: center; padding-top: 0.3rem; }
.panel-head { font-size: 0.9rem; letter-spacing: 0.08em; text-transform: uppercase; color: #5A6472;
  margin: 0.4rem 0 0.9rem 0; border-bottom: 1px solid #DCE2E0; padding-bottom: 0.3rem; }

/* smaller laptops: tighter margins and slightly smaller control text so the bottom row fits */
@media (max-width: 1500px) {
  [data-testid="stMainBlockContainer"], .block-container { padding-left: 1.5rem !important;
    padding-right: 1.5rem !important; }
  [data-testid="stWidgetLabel"] p, [data-baseweb="select"] div, [data-testid="stPopover"] button p,
  [data-testid="stBaseButton-segmented_control"] p, [data-testid="stBaseButton-segmented_controlActive"] p {
    font-size: 0.85rem !important; }
  h1.page-title { font-size: 1.75rem !important; }
  p.readout { font-size: 1.05rem !important; }
}
</style>""", unsafe_allow_html=True)

if "rule" not in st.session_state:
    # First visit: open on the question readers are most likely to have.
    st.session_state["preset"] = "Burnham reform from 2030"
    apply_preset()

# ---- run the model (session_state already holds every control's current value)
settings = {key: st.session_state[key] for key in DEFAULTS}
settings_items = tuple(sorted(settings.items()))
uncertain = settings["uncertainty"]
view = st.session_state["view"]
with st.spinner("Running the model"):
    results = run_uncertain(settings_items) if uncertain else run_deterministic(settings_items)


def final(name, measure, key="p50"):
    series = results[name][measure]
    return (series[key][-1] if uncertain else series[-1]) * 100


def first_year_needed(name):
    series = results[name]["saving"]
    path = series["p50"] if uncertain else series
    for year, value in zip(results[name]["years"], path):
        if value > 1e-9:
            return year
    return None


# ---- the readout sentence, for whichever view is showing
# Every number that moves with the controls is highlighted: teal for your scenario,
# red for the triple lock, dark for the gap between them and the target you set.
def scen_num(text):
    return f"<b class='scen'>{text}</b>"


def base_num(text):
    return f"<b class='base'>{text}</b>"


def gap_num(text):
    return f"<b class='num'>{text}</b>"


lead = "In the median future, " if uncertain else ""
if view == "Public debt":
    scen, base = final("scenario", "debt"), final("baseline", "debt")
    gap = base - scen
    if abs(gap) < 0.5:
        comparison = f"about the same as keeping the triple lock ({base_num(f'{base:.0f}%')})"
    elif gap > 0:
        comparison = (f"{gap_num(f'{gap:.0f} points')} lower than keeping the triple lock "
                      f"({base_num(f'{base:.0f}%')})")
    else:
        comparison = (f"{gap_num(f'{-gap:.0f} points')} higher than keeping the triple lock "
                      f"({base_num(f'{base:.0f}%')})")
    if scen >= 0:
        outcome = f"debt reaches {scen_num(f'{scen:.0f}% of GDP')}"
    else:
        outcome = f"debt is paid off entirely, leaving {scen_num(f'net assets of {-scen:.0f}% of GDP')}"
    sentence = f"{lead}public {outcome} in 2076 under your settings, {comparison}."
    if uncertain:
        lo, hi = final("scenario", "debt", "p5"), final("scenario", "debt", "p95")
        sentence += f" In 90% of futures it lands between {scen_num(f'{lo:.0f}%')} and {scen_num(f'{hi:.0f}%')}."
    elif RULES[settings["rule"]] in ("smoothed_earnings", "earnings"):
        sentence += (" <span class='aside'>With a steady economy this reform matches the triple lock; "
                     "turn on <b>Volatile economy</b> to see what it saves.</span>")
elif view == "Pension spending":
    pen_s, pen_b = final("scenario", "pension"), final("baseline", "pension")
    sentence = (f"{lead}State Pension spending is {scen_num(f'{pen_s:.1f}% of GDP')} in 2076 under your "
                f"settings, against {base_num(f'{pen_b:.1f}%')} under the triple lock (5% today). "
                f"A lower line means pensions grow more slowly than the economy.")
else:
    target = settings["debt_target"]
    y_s, y_b = first_year_needed("scenario"), first_year_needed("baseline")
    if y_s is None:
        sentence = (f"{lead}debt stays below {gap_num(f'{target:.0f}% of GDP')} to 2076 under your settings, "
                    "so no extra saving is needed.")
    else:
        sh_s = final("scenario", "saving")
        sentence = (f"{lead}holding debt at {gap_num(f'{target:.0f}% of GDP')} needs extra saving from "
                    f"{scen_num(y_s)}, reaching {scen_num(f'{sh_s:.1f}% of GDP')} "
                    f"(about {scen_num(f'£{sh_s / 100 * GDP_2026_27_BN:,.0f}bn')}) a year by 2076.")
    if y_b is None:
        sentence += " Under the triple lock, none would be needed."
    else:
        sh_b = final("baseline", "saving")
        sentence += (f" Keeping the triple lock: {base_num(f'{sh_b:.1f}%')} "
                     f"(about {base_num(f'£{sh_b / 100 * GDP_2026_27_BN:,.0f}bn')}), from {base_num(y_b)}.")
sentence = sentence[0].upper() + sentence[1:]


# ---- three columns: pension policy | title, readout, chart and view controls | the economy
left, centre, right = st.columns([1, 3.4, 1], gap="large")

with left:
    st.markdown("<p class='panel-head'>Pension policy</p>", unsafe_allow_html=True)
with left, st.container(key="leftpanel"):
    st.selectbox("Start from", list(PRESETS), key="preset", on_change=apply_preset,
                 help="Quick scenarios. Each one resets every control.")
    st.selectbox("How the pension rises", list(RULES), key="rule",
                 help="The uprating rule. Reforms apply from the year below; the triple lock applies before it.")
    reform_on = RULES[st.session_state["rule"]] != "triple_lock"
    st.slider("Reform starts in", 2027, 2060, key="reform_year", disabled=not reform_on)
    st.toggle("Means-test the pension", key="means_test",
              help="Withdraw the pension gradually from pensioners with private income above a threshold.")
    mt_on = st.session_state["means_test"]
    st.slider("Threshold (£ a week of other income)", 0.0, 600.0, step=5.0, key="threshold",
              format="£%.0f", disabled=not mt_on)
    st.slider("Taper (pence lost per £1 above it)", 0.0, 100.0, step=1.0, key="taper", format="%.0fp",
              disabled=not mt_on)
    with st.popover("More pension options", icon=":material/tune:", width="stretch"):
        st.slider("Floor", 0.0, 5.0, step=0.1, key="floor", format="%.1f%%",
                  help="Minimum annual rise under the triple and double locks. Currently 2.5%.")
        st.radio("Means-test threshold rises with", ["Pension uprating", "Earnings"], key="threshold_link",
                 horizontal=True, disabled=not mt_on)

with right:
    if st.button("How does this work?", icon=":material/menu_book:", type="primary", width="stretch",
                 help="The question, the findings and how the model is built"):
        story_panel()
    st.markdown("<p class='panel-head'>The economy</p>", unsafe_allow_html=True)
with right, st.container(key="rightpanel"):
    st.slider("Real GDP growth", 0.0, 3.0, step=0.1, key="real_growth", format="%.1f%%")
    st.slider("Inflation", 0.0, 6.0, step=0.1, key="inflation", format="%.1f%%")
    st.slider("Real earnings growth", -1.0, 3.0, step=0.1, key="productivity", format="%.1f%%")
    st.slider("Interest rate on debt", 0.0, 8.0, step=0.1, key="gilt", format="%.1f%%")
    with st.popover("More economy options", icon=":material/tune:", width="stretch"):
        st.slider("Pensioner population growth", 0.0, 2.0, step=0.05, key="pensioner_growth", format="%.2f%%")
        st.slider("Debt today (% of GDP)", 50.0, 150.0, step=0.5, key="start_debt", format="%.1f%%")
    if README_PDF.exists():
        st.download_button("Full write-up (PDF)", README_PDF.read_bytes(),
                           file_name="Pension-debt-model-Alexis-Laurent.pdf", mime="application/pdf",
                           icon=":material/download:", type="tertiary", width="stretch", key="pdf_side")

measure, title = {"Public debt": ("debt", "Public debt"),
                  "Pension spending": ("pension", "Pension spending"),
                  "Saving needed": ("saving", "Extra saving")}[view]
note = (f"Lines: median of {settings['runs']:,} simulated futures. Shading: middle 90%."
        if uncertain else "Steady inflation and earnings growth.")

with centre:
    st.markdown("<div class='page-head'><h1 class='page-title'>Pension uprating and UK public debt, 2026–2076</h1>"
                f"<p class='readout'>{sentence}</p></div>", unsafe_allow_html=True)
    with st.container(key="chartbox"):
        st.altair_chart(chart(results, measure, title, uncertain, note), width="stretch", height="stretch")

    # along the bottom of the chart: what to show, and how much uncertainty
    b_view, b_unc, b_vol, b_target = st.columns([2.5, 1.15, 1.0, 1.4], gap="medium",
                                                vertical_alignment="bottom")
    with b_view:
        st.segmented_control("Show", VIEWS, key="view", required=True, width="stretch")
    with b_unc:
        st.toggle("Volatile economy", key="uncertainty",
                  help="Runs the model on many random economic futures (Monte Carlo) and shades the "
                       "middle 90% of outcomes. Volatility is calibrated on 2011-2026 UK data.")
        unc_on = st.session_state["uncertainty"]
    with b_vol:
        with st.popover("Volatility", icon=":material/ssid_chart:", width="stretch",
                        disabled=not unc_on):
            st.select_slider("Simulated futures", [100, 250, 500, 1000], key="runs")
            st.slider("Inflation volatility (pp)", 0.0, 4.0, step=0.05, key="sd_inflation", format="%.2f")
            st.slider("Real earnings volatility (pp)", 0.0, 4.0, step=0.05, key="sd_productivity", format="%.2f")
    with b_target:
        st.slider("Debt target (% of GDP)", 60.0, 150.0, step=5.0, key="debt_target", format="%.0f%%",
                  disabled=view != "Saving needed",
                  help="Used by the 'Saving needed' view.")

# ---- footer
st.markdown(f"<p class='small-note footer'>Model and analysis by Alexis Laurent, BA Economics and International "
            f"Development, University of Sussex · <a href='{REPO_URL}' target='_blank'>Code on GitHub</a>"
            " · A stress test, not a forecast.</p>", unsafe_allow_html=True)
