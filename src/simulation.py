from src import params
from src.indicator import highest_triple_lock_value
import matplotlib.pyplot as plt
from src.means_test import average_means_tested_pension

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
    max_pension = params.MAX_PENSION,
    threshold = params.MEANS_TEST_THRESHOLD,
    taper_rate = params.TAPER_RATE,
    single_income_quintiles = params.SINGLE_INCOME_QUINTILES,
    couple_income_quintiles = params.COUPLE_INCOME_QUINTILES,
    single_weight = params.SINGLE_WEIGHT,
    couple_weight = params.COUPLE_WEIGHT
    ):

    n_gdp_growth = r_gdp + inflation
    average_earnings_growth = productivity_growth + inflation
    pensioner_expenditure = starting_pensioner_expenditure

    years = []
    pension_shares = []
    debts = []

    for year in range(first_year, last_year + 1):
        #print(f"Year: {year}", f"Pensioner Expenditure: {pensioner_expenditure}", f"Debt to GDP: {debt_to_gdp}")
        ratio = average_means_tested_pension(single_income_quintiles, couple_income_quintiles, single_weight, couple_weight, threshold, max_pension, taper_rate)/max_pension
        actual_expenditure = ratio * pensioner_expenditure
        years.append(year)
        pension_shares.append(actual_expenditure)
        debts.append(debt_to_gdp)
        tlock = 1 + highest_triple_lock_value(average_earnings_growth, inflation, tlock_floor)
        growth_factor = (tlock * (1 + pensioner_growth)/(1 + n_gdp_growth))
        primary_balance = starting_pensioner_expenditure - actual_expenditure
        debt_to_gdp = (debt_to_gdp * (1 + gilt_rate))/(1 + n_gdp_growth) - primary_balance
        pensioner_expenditure = growth_factor * pensioner_expenditure
        max_pension = max_pension * tlock
        threshold = threshold * tlock
        single_income_quintiles = [single_income_quintiles[i] * (1 + average_earnings_growth) for i in range(len(single_income_quintiles))]
        couple_income_quintiles = [couple_income_quintiles[i] * (1 + average_earnings_growth) for i in range(len(couple_income_quintiles))]
    return years, pension_shares, debts

if __name__ == "__main__":

    years, pension_shares, debts  = debt_projection(taper_rate=0)
    years_4, pension_shares_4, debts_4 = debt_projection(tlock_floor=0.04, taper_rate=0)
    years_mt, pension_shares_mt, debts_mt = debt_projection()
    years_mt_4, pension_shares_mt_4, debts_mt_4 = debt_projection(tlock_floor=0.04)

    plt.plot(years, debts, label="Triple Lock 2.5% Floor")
    plt.plot(years_4, debts_4, label="Triple Lock 4% Floor")
    plt.plot(years_mt, debts_mt, label="Means Test 2.5% Floor")
    plt.plot(years_mt_4, debts_mt_4, label="Means Test 4% Floor")
    plt.xlabel("Year")
    plt.ylabel("Debt to GDP (1.0 = 100%)")
    plt.title("UK Debt Projection 2026-2076")
    plt.legend()
    plt.show()

    