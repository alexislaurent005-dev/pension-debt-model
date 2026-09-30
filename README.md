# Means-Tested Pension vs. Triple Lock: A Debt-to-GDP Model

**[Open the interactive model](https://alexislaurent-pension-debt-model.streamlit.app/)**

Research project modelling the long-run impact on the UK's debt-to-GDP ratio of the current State Pension "triple lock" uprating rule, compared against a means-tested pension alternative.

**Status:** core model, scenario analysis and Monte Carlo complete; interactive app available. Research write-up in progress (see `findings.md`).

## Try the interactive model

**Live app: [https://alexislaurent-pension-debt-model.streamlit.app/](https://alexislaurent-pension-debt-model.streamlit.app/)**

Choose a pension uprating rule (including the triple lock reform announced in September 2026), switch on a means test, change the economic assumptions and simulate volatile inflation and earnings, then see how UK public debt responds to 2076.

To run it on your own computer:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Motivation

_(to be written as the project develops — the case for revisiting the triple lock's fiscal sustainability and how means-testing could compare)_

## Methodology

_(to be written — data sources, the triple lock and means-tested pension rules as modelled, and the debt accumulation identity used to translate pension spending into a debt-to-GDP path)_

## Repository structure

```
app.py      interactive front end (Streamlit)
src/        model code
data/       input data (OBR / ONS / DWP series)
tests/      unit tests
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Author

Alexis
