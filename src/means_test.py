def means_tested_pension(pensioner_extra_income, threshold, max_pension, taper_rate):
    pension = max(0, max_pension - taper_rate * max(0, pensioner_extra_income - threshold))
    return pension
