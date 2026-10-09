# Means-Tested Pension vs. Triple Lock: A Debt-to-GDP Model

**[Open the interactive model](https://alexislaurent-pension-debt-model.streamlit.app/)**

A Python model projecting how the design of the UK State Pension affects the long-run path of UK public debt, from 2026 to 2076.

## Summary

This project asks, 'How do the State Pension's uprating rule and eligibility design affect the long-run path of UK public debt?'. Using OBR, ONS, and DWP data, I built a model projecting long-run paths of UK public debt, from 2026 – 2076, comparing the current triple lock mechanism, my means-tested alternative, and the uprating reform announced by Prime Minister Andy Burnham in September 2026. Because the triple lock takes the highest of three possible rates of pension uprating, its cost varies with fluctuating inflation rates and earnings growth. So, I programmed a Monte Carlo simulation to include volatility into the model, generating a range of possible futures. They illustrated how the ratchet, taking the highest value that year, greatly increases the cost of the triple lock in the long run.

The largest effect came from volatility. Under the triple lock, volatility raised median 2076 debt to 288% of GDP, from 182% based on constant rates. Also, Burnham's reform from 2030 appears to save nothing under constant rates, but cuts median debt by 69 percentage points when including volatility. Therefore, the policy can be easily undervalued under models based on central assumptions. A means-tested pension would reduce pension expenditure by about 22% but does not remove the ratchet. Burnham's policy is complementary to a means-tested pension model, as together they can reduce median 2076 debt from 288% to 140% of GDP. These results are stress tests under simplified assumptions, not forecasts.

![Median debt paths across 1,000 simulated futures](docs/debt_paths.png)

*Figure 1. Median UK public debt under three pension policies across 1,000 simulated futures. Shaded areas show the range covering 90% of outcomes (5th to 95th percentile).*

## 1. Motivation

With an ever-tightening fiscal headroom for the UK, finding innovative ways to reduce government spending is growing increasingly important. So, when assigned a group project to reduce UK debt-to-GDP in an Advanced Macroeconomics module, I wanted to conjure a policy that didn't cling to hopes of growth. Instead, we investigated how the Treasury spends its revenue. Pensions, and the triple lock, stuck out as a significant, and fast-rising expenditure over the long run. We presented a means-tested pension, withdrawing the state pension for the top fifth of pensioner incomes. Whilst it did illustrate the potential savings, the model itself was crude, as a cliff-edge strongly disincentivised saving over the threshold. I wanted to see if I could improve our old model into something more robust. The new model replaces the cliff edge with a gradual 55% taper, is calibrated on published OBR, ONS and DWP data, simulates volatility, and comes with an interactive app for exploring scenarios.

## 2. Key terms

| Term | Meaning |
|---|---|
| Debt-to-GDP | Government debt as a share of the size of the economy. 100% means debt equals one year of national output. |
| Uprating | The yearly increase in the State Pension. |
| Triple lock | The current uprating rule: the pension rises each year by the highest of inflation, average earnings growth, or 2.5%. |
| Means test | Reducing a benefit for people with higher incomes from other sources. |
| Percentage points | The difference between two percentages: a fall from 288% to 219% is 69 percentage points. |
| Monte Carlo simulation | Running the model many times, each with a different random path for the economy, to see the range of possible outcomes. |
| Median, percentiles | The median is the middle outcome. The 5th and 95th percentiles bound the middle 90% of outcomes. |

## 3. Model

The model projects UK public debt as a share of GDP each year from 2026 to 2076. To isolate the effect of pension policy, all other government spending and tax revenue are held fixed as shares of GDP. Therefore, the debt paths show only the difference made by the pension, rather than a full forecast of the UK's public finances.

### Debt

Each year, debt grows with the interest paid on it, shrinks relative to a growing economy, and changes with the government's budget balance:

$$b_t = \frac{1 + r}{1 + g_t}\, b_{t-1} - pb_t$$

Where $b_t$ is debt-to-GDP in year $t$, $r$ is the interest rate on government debt (4.3%), $g_t$ is nominal GDP growth (1.5% real growth plus that year's inflation), and $pb_t$ is the primary balance: the budget surplus before interest payments. As only the pension changes, $pb_t$ is the gap between pension spending's starting share of GDP (5%) and its share in year $t$. Debt starts at 93.8% of GDP (ONS, August 2026).

Because the interest rate (4.3%) is higher than nominal growth (3.7%), debt grows faster than the economy unless the government runs a surplus. So, any extra pension spending compounds over time.

### Pension spending

Pension spending as a share of GDP, $s_t$, grows with the pension and the number of pensioners, relative to the economy:

$$s_t = s_{t-1} \cdot \frac{(1 + u_t)(1 + n)}{1 + g_t}$$

Where $u_t$ is the uprating rate and $n$ is pensioner population growth (0.85% a year, from ONS 2024-based projections). Spending therefore rises as a share of GDP whenever the pension and the pensioner population together grow faster than the economy. Earnings growth is productivity growth (1.4%) plus inflation (2.2%), following the OBR's long-run assumptions.

### Uprating rules

- **Triple lock:** the highest of inflation, earnings growth, or 2.5%.
- **Reform from 2030:** the triple lock applies until 2030, then one of three rules modelled on the September 2026 announcement, whose details are unpublished:
  - **Double lock:** the higher of inflation or 2.5%.
  - **Smoothed earnings link:** the double lock, plus a catch-up so the pension never falls behind an earnings-linked path starting in 2030. This is my interpretation of the announced adjustment to keep pace with earnings.
  - **Earnings only:** for comparison.

### Means-tested pension

Each pensioner receives the full new State Pension (£241.30 a week in 2026/27), minus 55p for every £1 of other income above a threshold of £238 a week:

$$P = \max\big(0,\ P_{max} - 0.55 \cdot \max(0,\ y - T)\big)$$

Where $P_{max}$ is the full pension, $y$ is a pensioner's other weekly income and $T$ is the threshold. The 55% rate is Universal Credit's taper, and the threshold is the Pension Credit Standard Minimum Guarantee. The pension is therefore withdrawn gradually, rather than all at once.

Pensioner incomes come from DWP *Pensioners' Incomes* (Table 4.4): ten income bands for single pensioners and couples, measured per person and weighted by each band's share of pensioners. Total spending is the full-pension cost, scaled by the average payment as a share of the full pension. Each year, the full pension and the threshold rise with the uprating rule (or the threshold with earnings, as an option), whilst private incomes rise with earnings.

### Uncertainty

Inflation and earnings rarely grow at a steady rate. So, I run a Monte Carlo simulation of 1,000 possible futures, each with its own path of inflation and productivity growth. Each year, both are drawn at random from normal distributions with the baseline averages (2.2% and 1.4%) and standard deviations calibrated on 2011/12 to 2026/27 data (2.55 and 2.45 percentage points). Every policy faces the same 1,000 futures (random seed 42), so differences between policies come from the policy, not from chance. Excluding the pandemic years from the calibration gives very similar results.

Full sources are listed in [`data/sources.md`](data/sources.md).

## 4. Results

### 4.1 Means testing lowers the level of spending

At today's parameters, the average means-tested payment is £187.93 a week, compared with the full £241.30. The means-tested system therefore costs about 78% of the current bill, lowering pension spending from 5% to 3.9% of GDP: a saving of roughly 22%.

The whole saving comes from the richest third of pensioners:

| Income band | Share of pensioners | Effect |
|---|---|---|
| Top-fifth singles | 6.7% | Lose the full pension |
| Top-fifth couples | 13.3% | Lose the full pension |
| Fourth-fifth couples | 13.3% | Lose about £38 a week |

About two-thirds of pensioners keep the full pension, as only substantial private income crosses the £238 threshold. So, the threshold decides both how much is saved and who pays for it. A lower threshold saves more, but reaches middle-income pensioners, for whom the 55% taper acts like a high tax on their savings.

With constant inflation and earnings growth, means testing cuts 2076 debt from 182% to 106% of GDP. Debt first falls, reaching its lowest point in the 2040s, before an ageing population pushes it back up. However, all paths eventually rise, as the interest rate on debt exceeds nominal GDP growth.

### 4.2 The ratchet: why volatility raises the triple lock's cost

The triple lock raises the pension by the highest of three rates each year, and every rise is kept. This creates a ratchet. The pension picks up whichever rate is high in a given year, but never falls back when that rate drops. Therefore, its cost depends on how much inflation and earnings fluctuate, not just on their averages. In economic terms, the maximum of several rates is a convex function, so its average exceeds the maximum of their averages (Jensen's inequality).

A simple test shows this. If inflation and earnings alternate between high and low years, but keep the same averages, the pension rises by about 3.9% a year instead of 3.6%. Consequently, 2076 debt reaches 206% of GDP instead of 182%. With volatility calibrated on 2011–2026 data, the effect is much larger:

| 2076 debt-to-GDP | 5th percentile | Median | 95th percentile |
|---|---|---|---|
| Triple lock | 212% | 288% | 397% |
| Means-tested | 148% | 212% | 310% |
| *Constant rates* | | *182% / 106%* | |

Both sources of volatility matter. Productivity volatility alone (the earnings-versus-inflation ratchet) gives a median of about 233%. Inflation volatility alone gives about 243%, through the 2.5% floor: when inflation is low, the pension still rises by 2.5% whilst the economy grows slowly. Excluding the pandemic years from the calibration lowers the medians by only 8–9 percentage points, leaving the gap between the policies unchanged.

The outcomes also overlap heavily, as the means test's 95th percentile exceeds the triple lock's median. This shows how economic uncertainty is as large as the policy choice itself.

### 4.3 The value of reform is invisible under central assumptions

| Universal pension, rule from 2030 | Constant rates | Monte Carlo median (5th–95th) |
|---|---|---|
| Triple lock (no reform) | 182% | 288% (212–397%) |
| Smoothed earnings link | 182% | 219% (157–311%) |
| Earnings only | 182% | 196% (135–280%) |
| Double lock | 116% | 183% (125–267%) |

At constant rates, earnings growth always exceeds inflation, so the triple lock already rises with earnings and a smoothed earnings link changes nothing. Under volatility, however, the same reform cuts median debt by 69 percentage points, because its whole effect is removing the ratchet. A costing based only on central assumptions would therefore record no saving at all.

How the earnings adjustment is defined is decisive. A pure double lock saves the most, but lets the pension fall steadily behind earnings. At constant rates, pension spending reaches about 4.5% of GDP by 2076 instead of 7.3%, a large cut in pensioners' living standards relative to workers. The smoothed version keeps the earnings link, whilst still removing most of the ratchet. However, as the triple lock applies until 2030, the reform cannot undo the ratchet built up before then.

### 4.4 Means testing and uprating reform are complements

Means testing gives almost no protection from the ratchet. When inflation and earnings alternate, it adds about 23 percentage points to 2076 debt, almost the same as the 24 under a universal pension. This is because the ratchet passes straight into the full pension, which two-thirds of pensioners still receive. Uprating the threshold with earnings, rather than with the pension, helps only slightly, lowering the Monte Carlo median from 212% to 198%.

The two policies therefore act on different things. Means testing lowers the *level* of spending, whilst uprating reform removes the *ratchet*. Combined, their effects add up:

| Monte Carlo median, 2076 debt | Universal | Means-tested |
|---|---|---|
| Triple lock | 288% | 212% |
| Smoothed earnings link from 2030 | 219% | 140% |

### 4.5 The saving needed to hold debt at 100% of GDP

Another way to read these results is the extra saving the government would need each year to stop debt rising above 100% of GDP. Pound figures are given at the size of today's economy (about £3.2 trillion).

| Saving needed by 2076 | Constant rates | Monte Carlo median |
|---|---|---|
| Triple lock | 2.9% of GDP (~£90bn), from 2034 | 7.7% (~£244bn), from 2036 |
| Smoothed earnings link | 2.9% (~£90bn), from 2034 | 3.9% (~£123bn), from 2038 |
| Smoothed earnings link + means test | 1.2% (~£39bn), from 2070 | 1.8% (~£56bn), from 2063 |

Because the interest rate exceeds growth, allowing debt to settle at a higher level only delays the saving needed and makes it larger. Holding debt at 150% of GDP under the triple lock needs 8.0% of GDP by 2076 in the median future, as a larger debt carries a permanently larger interest bill.

## 5. Limitations

### Debt Calculation

Like any economic model, mine comes with some assumptions that must be declared. Firstly, all other fiscal factors are frozen and assumed as constant over the 50-year period. Plainly, taxation and spending don't change. I chose this to focus on illustrating the isolated difference pension policy can make for UK debt-to-GDP, rather than a forecast. Similarly, interest rates do not change. As of writing (October 2026), growing UK debt has pushed gilts above 5.4%, which already far exceeds the model's 4.3% effective rate. If these higher rates persist, the model's debt paths are likely too low: at a 5.4% rate, triple lock debt reaches 280% of GDP by 2076, rather than 182%.

### Pension Spending

Also, pensioner growth is fixed at 0.85% per year to 2076. This rate is unlikely to remain constant with an increasingly ageing population projected beyond the ONS projections to 2049. Therefore, this model may underestimate the true cost of the triple lock.

### Monte Carlo

Simulating true future economic volatility is not as simple as generating 1,000 different futures under the parameters of today. Each year is drawn independently of the last, whilst real shocks, like the 2022–24 inflation spike, can last several years. Also, the inclusion of recent inflation shocks into long run predictions may overstate the volatility of future years. With technological breakthroughs in AI, and the ever-worsening climate crisis, those parameters could be wildly different soon. Currently, it's impossible to predict exactly what will happen in the next 5 years, let alone the next 50.

### Means Test

The means-tested pension assumes that nobody changes their behaviour. In reality, losing 55p for every £1 of private income acts like a 55% tax on savings, so some pensioners may save less, raising the cost of the means test. Furthermore, every eligible pensioner is assumed to claim, whilst real Pension Credit take-up is well below 100%. Lower take-up would increase the savings, but leave poorer pensioners who do not claim worse off. However, some cautious data choices, such as subtracting all benefit income from pensioner incomes, overstate means-tested spending, and therefore understate the savings. Couples are also counted as two pensioners, although 25% include a partner below State Pension age.

### Scope

Lastly, no government would let debt reach 288% of GDP without responding. These results are therefore stress tests, not forecasts. The 2030 reform is also my interpretation of a policy whose details are unpublished, and the National Care Service it would fund is not modelled. Ultimately, some of these limitations overstate the savings, whilst others understate them. So, the headline numbers are best read as rough sizes, rather than precise predictions.

## 6. Interactive model

**[alexislaurent-pension-debt-model.streamlit.app](https://alexislaurent-pension-debt-model.streamlit.app/)**

The app lets readers choose the uprating rule and reform year, the triple lock floor, a means test (threshold, taper rate and how the threshold rises), the economic assumptions, and the amount of volatility. It can also show the saving needed to hold debt at a chosen level. Every scenario is compared with today's triple lock in the same economy.

## 7. Reproducing the results

```bash
git clone https://github.com/alexislaurent005-dev/pension-debt-model.git
cd pension-debt-model
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python -m src.simulation        # constant-rate and alternating-rate scenarios
python -m src.montecarlo        # 1,000 simulated futures
streamlit run app.py            # interactive app
```

```
app.py              interactive front end (Streamlit)
src/params.py       baseline assumptions, each traced to a source
src/indicator.py    uprating rules (triple lock, double lock, earnings)
src/means_test.py   means-tested pension and average payment
src/simulation.py   debt and pension spending projection
src/montecarlo.py   random economic paths and simulation runs
src/calibration.py  volatility calibration from 2011–2026 data
data/sources.md     data sources and calibration notes
findings.md         full log of results
```

## 8. Data sources

- **OBR**, *Fiscal risks and sustainability*, July 2026: long-run growth, inflation, interest rate and pension spending projections
- **ONS**, *Public sector finances*, August 2026: starting debt (93.8% of GDP)
- **ONS**, *National population projections*, 2024-based: pensioner population growth
- **DWP**, *Pensioners' Incomes*, Table 4.4 (March 2026): pensioner income distribution
- **GOV.UK**, *Benefit and pension rates 2026 to 2027* and *Pension Credit*: full pension and threshold
- **House of Commons Library**, *State Pension triple lock*: uprating rule

Full citations and calibration notes are in [`data/sources.md`](data/sources.md).

## Author

Alexis
