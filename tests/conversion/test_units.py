"""Tests for unit conversion functions."""

import pytest

from foodlog.conversion.units import dv_percent_to_mcg, mcg_to_dv_percent


def test_dv_percent_to_mcg_basic() -> None:
    """Test basic %DV to mcg conversion."""
    # Vitamin A: DV = 900 mcg, 50% should be 450 mcg
    result = dv_percent_to_mcg(50.0, 900.0)
    assert result == 450.0

    # Vitamin D: DV = 20 mcg, 100% should be 20 mcg
    result = dv_percent_to_mcg(100.0, 20.0)
    assert result == 20.0

    # Calcium: DV = 1300000 mcg, 25% should be 325000 mcg
    result = dv_percent_to_mcg(25.0, 1300000.0)
    assert result == 325000.0


def test_dv_percent_to_mcg_zero() -> None:
    """Test %DV to mcg conversion with 0%."""
    result = dv_percent_to_mcg(0.0, 900.0)
    assert result == 0.0


def test_dv_percent_to_mcg_full() -> None:
    """Test %DV to mcg conversion with 100%."""
    result = dv_percent_to_mcg(100.0, 900.0)
    assert result == 900.0


def test_dv_percent_to_mcg_more_than_100() -> None:
    """Test %DV to mcg conversion with >100%."""
    result = dv_percent_to_mcg(150.0, 900.0)
    assert result == 1350.0


def test_mcg_to_dv_percent_basic() -> None:
    """Test basic mcg to %DV conversion."""
    # Vitamin A: DV = 900 mcg, 450 mcg should be 50%
    result = mcg_to_dv_percent(450.0, 900.0)
    assert result == 50.0

    # Vitamin D: DV = 20 mcg, 20 mcg should be 100%
    result = mcg_to_dv_percent(20.0, 20.0)
    assert result == 100.0

    # Calcium: DV = 1300000 mcg, 325000 mcg should be 25%
    result = mcg_to_dv_percent(325000.0, 1300000.0)
    assert result == 25.0


def test_mcg_to_dv_percent_zero() -> None:
    """Test mcg to %DV conversion with 0 mcg."""
    result = mcg_to_dv_percent(0.0, 900.0)
    assert result == 0.0


def test_mcg_to_dv_percent_zero_dv() -> None:
    """Test mcg to %DV conversion with 0 DV (edge case)."""
    result = mcg_to_dv_percent(450.0, 0.0)
    assert result == 0.0


def test_mcg_to_dv_percent_more_than_100() -> None:
    """Test mcg to %DV conversion with > 100%."""
    result = mcg_to_dv_percent(1350.0, 900.0)
    assert result == 150.0


def test_roundtrip_percent_to_mcg_to_percent() -> None:
    """Test that conversions are inverse operations."""
    # Start with a percent, convert to mcg, convert back
    original_percent = 75.0
    dv_amount = 900.0

    mcg = dv_percent_to_mcg(original_percent, dv_amount)
    back_to_percent = mcg_to_dv_percent(mcg, dv_amount)

    assert abs(back_to_percent - original_percent) < 0.0001


def test_roundtrip_mcg_to_percent_to_mcg() -> None:
    """Test that conversions are inverse operations."""
    # Start with mcg, convert to percent, convert back
    original_mcg = 675.0
    dv_amount = 900.0

    percent = mcg_to_dv_percent(original_mcg, dv_amount)
    back_to_mcg = dv_percent_to_mcg(percent, dv_amount)

    assert abs(back_to_mcg - original_mcg) < 0.0001
