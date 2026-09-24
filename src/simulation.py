from src import params
from src.indicator import highest_triple_lock_value

def debt_projection(    
    starting_pensioner_expenditure = params.PENSION_EXPENDITURE, 
    debt_to_gdp = params.STARTING_DEBT_TO_GDP,
    r_gdp = params.REAL_GDP_GROWTH,
    inflation = params.INFLATION_RATE,
    gilt_rate = params.GILT_RATE,
    productivity_growth = params.PRODUCTIVITY_GROWTH,
    tlock_floor = params.TRIPLE_LOCK_FLOOR,
    pensioner_growth = params.PENSIONER_GROWTH,
    first_year = params.FIRST_YEAR,
    last_year = params.FINAL_YEAR,
    ):

    n_gdp_growth = r_gdp + inflation
    average_earnings_growth = productivity_growth + inflation
    pensioner_expenditure = starting_pensioner_expenditure

    for year in range(first_year, last_year + 1):
        print(f"Year: {year}", f"Pensioner Expenditure: {pensioner_expenditure}", f"Debt to GDP: {debt_to_gdp}")
        tlock = 1 + highest_triple_lock_value(average_earnings_growth, inflation, tlock_floor)
        growth_factor = (tlock * (1 + pensioner_growth)/(1 + n_gdp_growth))
        primary_balance = starting_pensioner_expenditure - pensioner_expenditure
        debt_to_gdp = (debt_to_gdp * (1 + gilt_rate))/(1 + n_gdp_growth) - primary_balance
        pensioner_expenditure = growth_factor * pensioner_expenditure

debt_projection()
debt_projection(tlock_floor=0.04)