from src import params
from src.indicator import highest_triple_lock_value, uprating_rate
import matplotlib.pyplot as plt
from src.means_test import average_means_tested_pension

def debt_projection(    
    starting_pensioner_expenditure = params.PENSION_EXPENDITURE, 
    debt_to_gdp = params.STARTING_DEBT_TO_GDP,
    r_gdp = params.REAL_GDP_GROWTH,
    inflation = params.INFLATION_PATH,
    gilt_rate = params.GILT_RATE,
    productivity_growth = params.PRODUCTIVITY_PATH,
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
    couple_weight = params.COUPLE_WEIGHT,
    threshold_uprating = "pension",
    uprating_rule = "triple_lock",
    reform_year = None
    ):

   
    pensioner_expenditure = starting_pensioner_expenditure
    earnings_index = None  # only used by the "smoothed_earnings" rule

    years = []
    pension_shares = []
    debts = []

    for year in range(first_year, last_year + 1):
        #print(f"Year: {year}", f"Pensioner Expenditure: {pensioner_expenditure}", f"Debt to GDP: {debt_to_gdp}")
        year_values = year - first_year
        n_gdp_growth = r_gdp + inflation[year_values]
        average_earnings_growth = productivity_growth[year_values] + inflation[year_values]
        ratio = average_means_tested_pension(single_income_quintiles, couple_income_quintiles, single_weight, couple_weight, threshold, max_pension, taper_rate)/max_pension
        actual_expenditure = ratio * pensioner_expenditure
        years.append(year)
        pension_shares.append(actual_expenditure)
        debts.append(debt_to_gdp)
        if reform_year is None or year < reform_year:
            rule_this_year = "triple_lock"
        else:
            rule_this_year = uprating_rule

        if rule_this_year == "smoothed_earnings":
            if earnings_index is None:
                earnings_index = max_pension
            earnings_index = earnings_index * (1 + average_earnings_growth)
            double_locked = max_pension * (1 + max(tlock_floor, inflation[year_values]))
            tlock = max(double_locked, earnings_index) / max_pension
        else:
            tlock = 1 + uprating_rate(rule_this_year, average_earnings_growth, inflation[year_values], tlock_floor)
        growth_factor = (tlock * (1 + pensioner_growth)/(1 + n_gdp_growth))
        primary_balance = starting_pensioner_expenditure - actual_expenditure
        debt_to_gdp = (debt_to_gdp * (1 + gilt_rate))/(1 + n_gdp_growth) - primary_balance
        pensioner_expenditure = growth_factor * pensioner_expenditure
        max_pension = max_pension * tlock
        if threshold_uprating == "earnings":
            threshold = threshold * (1 + average_earnings_growth)
        else:
            threshold = threshold * tlock
        single_income_quintiles = [single_income_quintiles[i] * (1 + average_earnings_growth) for i in range(len(single_income_quintiles))]
        couple_income_quintiles = [couple_income_quintiles[i] * (1 + average_earnings_growth) for i in range(len(couple_income_quintiles))]
    return years, pension_shares, debts

if __name__ == "__main__":

    cycled_inflation = []
    cycled_productivity = []

    for index in range(params.FIRST_YEAR, params.FINAL_YEAR + 1):
        if index % 2 == 0:
            cycled_inflation.append(0.032)
            cycled_productivity.append(-0.006)
        else:
            cycled_inflation.append(0.012)
            cycled_productivity.append(0.034)
    
    years, pension_shares, debts  = debt_projection(taper_rate=0)
    years_4, pension_shares_4, debts_4 = debt_projection(tlock_floor=0.04, taper_rate=0)
    years_mt, pension_shares_mt, debts_mt = debt_projection()
    years_mt_4, pension_shares_mt_4, debts_mt_4 = debt_projection(tlock_floor=0.04)
    years_cyc, pension_shares_cyc, debts_cyc = debt_projection(tlock_floor=0.025, taper_rate=0, inflation=cycled_inflation, productivity_growth=cycled_productivity)
    years_cyc_mt, pension_shares_cyc_mt, debts_cyc_mt = debt_projection(tlock_floor=0.025, inflation=cycled_inflation, productivity_growth=cycled_productivity)
    print("Triple Lock 2.5% Floor:", debts[-1])
    print("Triple Lock 4% Floor:", debts_4[-1])
    print("Means Test 2.5% Floor:", debts_mt[-1])
    print("Means Test 4% Floor:", debts_mt_4[-1])
    print("Cycled Inflation and Productivity:", debts_cyc[-1])
    print("Cycled Inflation and Productivity (Means Test):", debts_cyc_mt[-1])

    # Threshold uprated with earnings instead of the pension (findings section 5)
    print("Means Test 2.5% Floor, threshold by earnings:", debt_projection(threshold_uprating="earnings")[2][-1])
    print("Means Test 4% Floor, threshold by earnings:", debt_projection(tlock_floor=0.04, threshold_uprating="earnings")[2][-1])
    print("Cycled Means Test, threshold by earnings:", debt_projection(inflation=cycled_inflation, productivity_growth=cycled_productivity, threshold_uprating="earnings")[2][-1])

    # Uprating reforms from April 2030 (findings section 6)
    for rule in ["double_lock", "smoothed_earnings", "earnings", "cpi"]:
        constant = debt_projection(taper_rate=0, uprating_rule=rule, reform_year=2030)[2][-1]
        cycled = debt_projection(taper_rate=0, uprating_rule=rule, reform_year=2030, inflation=cycled_inflation, productivity_growth=cycled_productivity)[2][-1]
        print(f"Reform from 2030 ({rule}), universal: constant rates {constant:.3f}, cycled {cycled:.3f}")

    plt.plot(years, debts, label="Triple Lock 2.5% Floor")
    plt.plot(years_4, debts_4, label="Triple Lock 4% Floor")
    plt.plot(years_mt, debts_mt, label="Means Test 2.5% Floor")
    plt.plot(years_mt_4, debts_mt_4, label="Means Test 4% Floor")
    plt.plot(years_cyc, debts_cyc, label="Cycled Inflation and Productivity")
    plt.plot(years_cyc_mt, debts_cyc_mt, label="Cycled Inflation and Productivity (Means Test)")
    plt.xlabel("Year")
    plt.ylabel("Debt to GDP (1.0 = 100%)")
    plt.title("UK Debt Projection 2026-2076")
    plt.legend()
    plt.show()

    