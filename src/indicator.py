def highest_triple_lock_value(average_earnings_growth, inflation_rate, floor):
    return max(floor, average_earnings_growth, inflation_rate)


def double_lock_value(inflation_rate, floor):
    """Double lock: the higher of inflation or the floor (earnings dropped)."""
    return max(floor, inflation_rate)


def uprating_rate(rule, average_earnings_growth, inflation_rate, floor):
    """Annual uprating rate for the State Pension under a given rule.

    rule: "triple_lock" (earnings, inflation or floor), "double_lock"
    (inflation or floor), "earnings" (earnings only) or "cpi" (inflation only).
    The "smoothed_earnings" rule needs the pension's level history, so it is
    handled inside debt_projection rather than here.
    """
    if rule == "triple_lock":
        return highest_triple_lock_value(average_earnings_growth, inflation_rate, floor)
    elif rule == "double_lock":
        return double_lock_value(inflation_rate, floor)
    elif rule == "earnings":
        return average_earnings_growth
    elif rule == "cpi":
        return inflation_rate
    else:
        raise ValueError(f"Unknown uprating rule: {rule}")
