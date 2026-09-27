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