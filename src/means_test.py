def means_tested_pension(pensioner_extra_income, threshold, max_pension, taper_rate):
    pension = max(0, max_pension - taper_rate * max(0, pensioner_extra_income - threshold))
    return pension

def average_means_tested_pension(single_incomes, couple_incomes, single_weight, couple_weight, threshold, max_pension, taper_rate):
    total = 0
    for income in single_incomes:
        total += means_tested_pension(income, threshold, max_pension, taper_rate) * single_weight
    for income in couple_incomes:
        total += means_tested_pension(income, threshold, max_pension, taper_rate) * couple_weight
    return total