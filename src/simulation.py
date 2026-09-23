from src import params
from src.indicator import highest_triple_lock_value

pensioner_expenditure = params.PENSION_EXPENDITURE

debt_to_gdp = params.STARTING_DEBT_TO_GDP

for year in range(params.FIRST_YEAR, params.FINAL_YEAR + 1):
    print(f"Year: {year}", f"Pensioner Expenditure: {pensioner_expenditure}", f"Debt to GDP: {debt_to_gdp}")
    tlock = 1 + highest_triple_lock_value(params.AVERAGE_EARNINGS_GROWTH, params.INFLATION_RATE, params.TRIPLE_LOCK_FLOOR)
    pensioner_growth = (tlock * (1 + params.PENSIONER_GROWTH)/(1 + params.NOMINAL_GDP_GROWTH))
    primary_balance = params.PENSION_EXPENDITURE - pensioner_expenditure
    debt_to_gdp = (debt_to_gdp * (1 + params.GILT_RATE))/(1 + params.NOMINAL_GDP_GROWTH) - primary_balance
    pensioner_expenditure = pensioner_growth * pensioner_expenditure