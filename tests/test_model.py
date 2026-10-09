"""Checks that the model reproduces its published results.

These tests only call the model's functions; they do not change them.
Run with: python -m pytest
"""
import pytest

from src.indicator import highest_triple_lock_value
from src.means_test import means_tested_pension
from src.simulation import debt_projection


def test_triple_lock_picks_highest_rate():
    # earnings highest, then the 2.5% floor highest
    assert highest_triple_lock_value(0.036, 0.022, 0.025) == 0.036
    assert highest_triple_lock_value(0.010, 0.012, 0.025) == 0.025


def test_means_test_examples():
    # below the threshold: full pension
    assert means_tested_pension(100, 238, 241.30, 0.55) == pytest.approx(241.30)
    # £62 above the threshold: lose 55% of £62
    assert means_tested_pension(300, 238, 241.30, 0.55) == pytest.approx(207.20)
    # far above the threshold: pension falls to zero, never negative
    assert means_tested_pension(800, 238, 241.30, 0.55) == 0


def test_baseline_2076_debt():
    # findings.md section 2: 182% (triple lock) and 106% (means test)
    assert debt_projection(taper_rate=0)[2][-1] == pytest.approx(1.8235, abs=1e-3)
    assert debt_projection()[2][-1] == pytest.approx(1.0579, abs=1e-3)


def test_threshold_rules_match_at_constant_rates():
    # findings.md section 5: identical when the triple lock equals earnings growth
    by_pension = debt_projection()[2][-1]
    by_earnings = debt_projection(threshold_uprating="earnings")[2][-1]
    assert by_pension == pytest.approx(by_earnings)
