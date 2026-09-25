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
