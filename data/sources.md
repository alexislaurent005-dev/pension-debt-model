# Data Sources & Calibration

This project is calibrated on real published UK fiscal data rather than
invented figures. Every constant used in `src/params.py` traces back to one
of the sources below.

## State Pension triple lock (uprating rule)

- In force since 2011/12 (introduced in the Coalition Government's 2010 Budget)
- Each year, the State Pension is uprated by the **highest** of: CPI inflation,
  average earnings growth, or a 2.5% floor
- Source: House of Commons Library, "State Pension triple lock"
  — https://commonslibrary.parliament.uk/research-briefings/cbp-7812/

## OBR long-term fiscal projections

Office for Budget Responsibility, *Fiscal risks and sustainability* — July 2026
— https://obr.uk/frs/fiscal-risks-and-sustainability-july-2026/

- Public sector net debt: ~95% of GDP by 2030–31 in the baseline, moving onto
  an "unsustainable upward trajectory" over the 50-year horizon without policy
  change (this is a scenario illustrating fiscal pressure, not a forecast)
- State Pension spending: **5% of GDP by 2030–31, rising to ~9% of GDP by
  2075–76** under the triple lock; ~7% of GDP by 2075–76 if uprated by average
  earnings only instead — this is the number our baseline model tries to
  reproduce from first principles
- Baseline economic assumptions: real GDP growth 1.5%/yr, GDP deflator
  inflation 2.2%/yr, gilt rate (effective interest on government debt) 4.3%,
  population growth ~0%/yr (peaks mid-2050s then declines)

## Current debt-to-GDP starting point

- UK public sector net debt: **93.8% of GDP** as of August 2026
- Source: ONS, *Public sector finances, UK: August 2026*
  — https://www.ons.gov.uk/economy/governmentpublicsectorandtaxes/publicsectorfinance/bulletins/publicsectorfinances/august2026

## Pensioner population growth (demographics)

- ONS 2024-based national population projections: the pensionable-age
  population is projected to grow **23.7% between mid-2024 and mid-2049**
  (12.4m → 15.3m) — the largest growth of any life-stage group, driven by
  post-WW2 birth cohorts reaching older ages and rising life expectancy.
  Annualised, that's ~0.85%/year compound, which is what this model applies
  as a constant rate across the full 2026–2076 horizon.
- Source: ONS, *National population projections* (2024-based)
  — https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/bulletins/nationalpopulationprojections/2024based
- **Limitation:** the ONS figure only covers to 2049; holding that rate
  constant to 2076 is a simplifying assumption, and the ONS's own cohort/
  life-expectancy modelling is more detailed than a single constant growth
  rate can capture — this is the main reason this model's spend-to-GDP path
  is directionally right but doesn't land exactly on the OBR's own ~9% of
  GDP by 2075–76 figure.

## Means-tested design reference point

- Pension Credit — the UK's existing means-tested top-up for pensioners —
  guarantees a minimum weekly income of **£238 (single) / £363.25 (couple)**,
  operating as a top-up to that floor for anyone whose other income falls
  short of it
- Source: GOV.UK, "Pension Credit: What you'll get"
  — https://www.gov.uk/pension-credit/what-youll-get
- Rather than Pension Credit's real pound-for-pound cliff-edge withdrawal,
  this model tapers entitlement gradually above the threshold, using
  Universal Credit's current withdrawal rate of **55%** (55p withdrawn per
  £1 of other income) — a deliberate design choice, not a Pension Credit
  feature
- Source: Turn2us, "Universal Credit income: How your earnings affect UC"
  — https://www.turn2us.org.uk/get-support/information-for-your-situation/universal-credit-uc-income-and-capital/universal-credit-uc-earnings

## Modelling simplification (stated as a limitation)

This model isolates the *marginal* effect of the pension uprating policy
choice on debt-to-GDP: every other primary balance item (day-to-day spending,
tax revenue, other benefits) is held fixed at its current share of GDP, so the
debt path shown reflects only the divergence caused by the pension policy
choice — not a full fiscal forecast. Average earnings growth is derived as
productivity growth + inflation (1.4% + 2.2% ≈ 3.6% nominal), since the OBR
report did not give a single explicit long-run earnings figure in the
sections fetched for this project.
