# Findings log

Running notes on model results, to feed into the README write-up.

## 1. Starting cost of the means-tested pension (25 Sept 2026)

**Setup:** max pension £241.30/wk, threshold £238/wk of other income,
55% taper, DWP Table 4.4 income bands weighted by people (2 per couple).

**Result:** average payment **£187.93/wk** vs the full **£241.30/wk**
→ ratio **≈ 0.78**. The means-tested system would cost ~78% of the current
bill: roughly **3.9% of GDP instead of 5%**, a **~22% saving**.

**Who pays for the saving:** only 3 of 10 income bands lose anything:

| Band | Share of pensioners | Effect |
|---|---|---|
| Top-fifth singles | 6.7% | Lose full pension |
| Top-fifth couples | 13.3% | Lose full pension |
| Fourth-fifth couples | 13.3% | Lose ~£38/wk |

About **two-thirds of pensioners keep the full pension**; the whole saving
comes from the richest third. This follows from the £238 threshold being
high enough that only substantial private income triggers the taper.

**Policy trade-off (for write-up):** a lower threshold saves more but
starts reducing pensions for middle-income pensioners, where the 55% taper
also acts as a high effective marginal tax rate on their savings. The
threshold decides both *how much* is saved and *who* pays: the obvious
first slider for the control panel.

**Open question:** how means-tested spending should grow over time
(uprating of max pension and threshold; growth in private incomes).

## 2. Debt paths: triple lock vs means test (25 Sept 2026)

**Setup:** rule B uprating (max pension and threshold × triple lock;
private incomes × earnings growth). Triple lock runs use `taper_rate=0`,
which reproduces the original model exactly (regression test passed).

**Approximate debt-to-GDP in 2076 (read from chart):**

| Scenario | 2.5% floor | 4% floor |
|---|---|---|
| Triple lock (universal) | ~182% | ~218% |
| Means-tested (55% taper) | ~106% | ~140% |

FIRST RESULTS:
Triple Lock 2.5% Floor: 1.823522712602586
Triple Lock 4% Floor: 2.1774212108604996
Means Test 2.5% Floor: 1.057949376730886
Means Test 4% Floor: 1.3976036636157416

**Findings:**
- Means testing cuts 2076 debt by ~76pp in the baseline, a much larger
  effect than the choice of triple lock floor (~36pp)
- Means-tested debt falls at first (immediate ~1.1% of GDP annual saving),
  bottoming out in the 2040s before demographic pressure pushes it up
- A 4% floor adds ~34pp even under means testing: two-thirds of pensioners
  still receive the full triple-locked pension, so means testing barely
  insulates the budget from a more generous uprating rule
- The means test weakens over time under the 4% floor: the pension and
  threshold outgrow private incomes, pulling richer pensioners back
  under the threshold
- All paths eventually rise because the gilt rate (4.3%) exceeds nominal
  GDP growth (3.7%), so primary deficits compound (r > g)

**To do:** replace chart readings with exact printed values.

## 3. The triple lock ratchet (27 Sept 2026)

**Setup:** triple lock, 2.5% floor, `taper_rate=0`. Inflation and earnings
alternate each year (inflation 3.2% / 1.2%, earnings 2.6% / 4.6%), keeping
the same averages as the baseline (2.2% and 3.6%).

**Result:** debt in 2076 is **206% of GDP**, vs **182%** with constant
rates: **~24pp of extra debt from fluctuation alone**, about two-thirds
of the effect of raising the floor to 4% (218%).

**Why:** the triple lock takes the highest of earnings, inflation and 2.5%
each year and never gives it back. In this cycle it uprates by 3.2% and
4.6% in alternate years (average 3.9%), vs 3.6% with constant rates.
The pension ratchets up faster than earnings in the same average economy.
This is a key reason constant-rate projections understate the triple
lock's cost.


**Means test under the same cycle:** debt in 2076 is **129% of GDP**, vs
**106%** with constant rates: **~23pp from the ratchet**, almost the same
as the ~24pp under the triple lock. Means testing gives almost no
protection from the ratchet, because:
- the ratchet passes straight into the maximum pension, which ~two-thirds
  of pensioners receive in full; and
- the maximum pension and threshold (triple-locked, avg 3.9%) outgrow
  private incomes (earnings, avg 3.6%), pulling richer pensioners back
  under the threshold and eroding the means test over time

**Policy lesson:** means testing lowers the *level* of spending; only
reforming the uprating rule removes the *ratchet*. Controlling long-run
costs needs both levers. (To test later: uprating the threshold with
earnings rather than the triple lock.)

## 4. Monte Carlo: calibrated volatility (28 Sept 2026)

**Setup:** 1,000 random futures (seed 42). Each year, inflation and
productivity are drawn independently from normal distributions with the
baseline means (2.2%, 1.4%) and SDs calibrated from triple lock inputs
2011/12–2026/27 (inflation 2.55pp, productivity 2.45pp). Both policies face
the same 1,000 futures.

**2076 debt-to-GDP:**

| | 5th pct | Median | 95th pct |
|---|---|---|---|
| Triple lock | 212% | 288% | 397% |
| Means test | 148% | 212% | 310% |
| (Constant rates) | | 182% / 106% | |

**Findings:**
- Volatility raises median triple lock debt by ~106pp over constant rates.
  An independent replication decomposed this: productivity volatility alone
  (earnings vs inflation ratchet) gives a median of ~233%; inflation
  volatility alone gives ~243%, via the **2.5% floor**: when inflation falls
  below 2.5%, the pension still rises 2.5% while nominal GDP grows slowly
- Means testing saves a stable ~76pp at the median, the same as under
  constant rates, but cannot offset the ratchet
- The distributions overlap heavily: the means test's 95th percentile (310%)
  exceeds the triple lock's median. Uncertainty is as large as the policy choice

**Caveats:** a stress test, not a forecast. It applies 2011–2026 volatility
(including a rare inflation shock) independently every year for 50 years,
with no persistence, mean reversion or policy response.

**Sensitivity: pandemic years excluded** (inflation SD 2.64pp, productivity
SD 2.16pp; same seed):

| | 5th pct | Median | 95th pct |
|---|---|---|---|
| Triple lock | 207% | 280% | 391% |
| Means test | 142% | 203% | 301% |

Medians fall by only ~8–9pp and the policy gap is unchanged (~77pp), so the
results are robust to excluding the Covid-distorted earnings years. The high
volatility comes mainly from the genuine 2022–24 inflation shock.

## 5. Threshold uprated with earnings instead of the pension (30 Sept 2026)

**Question:** part of the means test's erosion under the ratchet came from the
threshold (uprated with the pension) outgrowing private incomes (uprated with
earnings). What if the threshold follows earnings instead?
(`threshold_uprating="earnings"` in `debt_projection`.)

| Means test, 2076 debt | Threshold follows pension | Threshold follows earnings |
|---|---|---|
| 2.5% floor, constant rates | 105.8% | 105.8% (identical, as predicted) |
| 4% floor | 139.8% | 135.9% |
| Cycled economy | 128.9% | 126.0% |
| Monte Carlo median | 212% | 198% |

**Finding:** with constant rates the two rules are identical (the triple lock
equals earnings growth), confirming the model logic. Linking the threshold
to earnings recovers only ~3-4pp in deterministic scenarios and ~14pp at the
Monte Carlo median. Most of the ratchet's cost flows through the **maximum
pension itself**, which two-thirds of pensioners receive in full, not
through threshold erosion. Fixing the means test's design is worth doing,
but it is not a substitute for reforming the uprating rule.

## 6. Uprating reform from April 2030: the Burnham announcement (30 Sept 2026)

**Context:** in his first conference speech as Prime Minister (29 Sept 2026),
Andy Burnham announced that the triple lock will be kept until April 2030,
then replaced by a double lock (inflation or 2.5%) with a longer-term
adjustment to keep pace with earnings, to help fund a National Care Service.
The detail of the earnings adjustment has not been published, so three
versions are modelled from 2030 (triple lock applies 2026-2029 in all):

- **double_lock**: max(inflation, 2.5%) only (upper bound on savings)
- **smoothed_earnings**: double lock each year, plus a catch-up so the pension
  never falls behind an earnings-linked path started in 2030 (our reading of
  the announced adjustment; similar in spirit to a "smoothed earnings link")
- **earnings**: earnings growth only (for comparison)

**2076 debt-to-GDP, universal pension:**

| Rule from 2030 | Constant rates | Cycled economy | Monte Carlo median (5th-95th) |
|---|---|---|---|
| Triple lock (no reform) | 182% | 206% | 288% (212-397%) |
| Smoothed earnings (Burnham reading) | 182% | 184% | 219% (157-311%) |
| Earnings only | 182% | 183% | 196% (135-280%) |
| Pure double lock | 116% | 138% | 183% (125-267%) |

**Monte Carlo medians with the means test added:** triple lock 212%,
smoothed earnings 140%, earnings only 119%, double lock 106%.

**Findings:**
- **The value of the reform is invisible under constant assumptions.** With
  constant rates, earnings always beats inflation, so a smoothed earnings link
  saves nothing (182% either way). Under realistic volatility it cuts median
  2076 debt by ~69pp, because its whole effect is removing the ratchet. A
  costing based only on central assumptions would badly understate it.
- **What the "keep pace with earnings" detail means is decisive.** A pure
  double lock saves far more (median 183%) but lets the pension fall steadily
  relative to earnings (pension spending ~4.5% of GDP by 2076 at constant
  rates vs ~7.3%), a large cut in pensioners' relative living standards. The
  smoothed version keeps the earnings link and still removes most of the
  ratchet.
- **Uprating reform and means testing are complementary.** Each alone lowers
  the median by ~70-76pp; together (smoothed earnings + means test) the median
  falls from 288% to 140%.
- **Timing matters:** the triple lock still applies until 2030, so the reform
  cannot undo the ratchet accumulated before then.

**Caveats:** the smoothed-earnings rule is an interpretation of an announced
policy whose details are unpublished; the model covers debt effects only, not
the National Care Service spending the savings would fund.

## 7. Interactive app (30 Sept 2026)

Live at https://alexislaurent-pension-debt-model.streamlit.app/ (Streamlit Community Cloud, deployed from `main`).

`app.py` is a Streamlit front end. It imports `debt_projection` and
`generate_random_paths` from `src/` and adds controls and charts only; no
model code was changed. Readers can choose the uprating rule and reform year,
the floor, a means test (threshold, taper, threshold uprating), the economic
assumptions and Monte Carlo volatility. The page always compares the chosen
scenario with today's triple lock in the same economy.

It opens on the Burnham reform with volatility switched on (1,000 futures,
seed 42), reproducing section 6: median 2076 debt 219% vs 288% under the
triple lock. With volatility off, the page explains why a smoothed earnings
link looks identical to the triple lock at constant rates.

Checks: all presets and toggles tested with Streamlit's testing tool; figures
match sections 2 and 6 exactly; layout checked at desktop and phone widths.

## 8. Saving needed to hold debt at 100% of GDP (1 Oct 2026)

**Method:** the app rebuilds each debt path with the same identity as
`debt_projection` (reproducing it exactly when no target applies) and, in any
year where debt would end above the target, adds the extra primary surplus
needed to hold it there. Pounds use OBR nominal GDP for 2026-27 (~£3.2tn), i.e.
each year's share of GDP at today's size of the economy.

**Extra saving needed by 2076 to hold debt at 100% of GDP:**

| Policy | Constant rates | Monte Carlo median |
|---|---|---|
| Triple lock | 2.9% of GDP (~£90bn); needed from 2034 | 7.7% (~£244bn); from 2036 |
| Smoothed earnings link from 2030 | 2.9% (~£90bn); from 2034 | 3.9% (~£123bn); from 2038 |
| Smoothed earnings link + means test | — | 1.8% (~£56bn); from 2063 |

**Findings:**
- At constant rates the triple lock's requirement is the pension overspend
  (7.3% - 5% of GDP) plus the interest-growth gap on debt held at 100%
  ((4.3% - 3.7%) / 1.037 x 100% ≈ 0.6% of GDP), a useful check on the logic.
- Under volatility, keeping the triple lock means finding ~£244bn a year (in
  today's terms) by 2076 to stop debt rising above 100% of GDP; the
  smoothed-earnings reform halves that, and adding a means test cuts it to
  ~£56bn and delays the need until the 2060s.
- Because r > g, a higher debt ceiling delays the saving but raises the
  eventual requirement (e.g. holding at 150% under the triple lock needs 8.0%
  of GDP by 2076 in the median future, vs 7.7% at 100%): a larger debt carries
  a permanently larger interest burden.

## App redesign: one screen (9 Oct 2026)

Reworked `app.py` so the whole model fits on one screen without scrolling,
for readers with no economics background. No model code in `src/` changed,
and the model-calling functions in `app.py` are unchanged.

- **Layout:** full width with side margins. The title and readout sit centred
  above the chart, which stretches to fill the window height; pension policy
  controls run down the left, the economy down the right, and the chart view,
  volatility and debt target sit under the chart. Less-used controls (the floor, threshold uprating, pensioner
  growth, starting debt, number of futures, volatility sizes) sit behind
  "More options" pop-overs.
- **One chart, three views:** public debt, pension spending, or the saving
  needed to hold debt at a target, chosen under the chart. The readout
  sentence above the chart changes with the view.
- **Story panel:** all the explanation (the question, the ratchet, findings,
  how the model works, limitations, key terms) moved into a panel that slides
  out from the right via "How does this work?".
- **Write-up:** the README PDF is in `docs/README.pdf`, downloadable from the
  panel and the footer.
- Credit corrected to BA Economics and International Development.
- `requirements.txt` now needs Streamlit 1.65+, for the right-hand panel.
