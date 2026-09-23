from src import params
from src.indicator import highest_triple_lock_value

pensioner_expenditure = params.PENSION_EXPENDITURE
tlock = 1 + highest_triple_lock_value(params.AVERAGE_EARNINGS_GROWTH, params.INFLATION_RATE, params.TRIPLE_LOCK_FLOOR)

for year in range(params.FIRST_YEAR, params.FINAL_YEAR + 1):
    print(f"Year: {year}", pensioner_expenditure)
    pensioner_expenditure = tlock * (1 + params.PENSIONER_GROWTH)/(1 + params.NOMINAL_GDP_GROWTH) * pensioner_expenditure
