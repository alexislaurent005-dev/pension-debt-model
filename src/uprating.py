def indicator(average_earnings_growth, inflation_rate, floor):
    return max(floor, average_earnings_growth, inflation_rate)


print(indicator(average_earnings_growth=0.014, inflation_rate=0.022, floor=0.025))
print(indicator(average_earnings_growth=0.09, inflation_rate=0.098, floor=0.028))