def highest_triple_lock_value(average_earnings_growth, inflation_rate, floor):
    return max(floor, average_earnings_growth, inflation_rate)
