"""Tests for live_ratio_calculator."""
import pytest

from foodlog.gui.components.live_ratio_calculator import compute_live_ratios


class TestComputeLiveRatios:
    """Test compute_live_ratios()."""

    def test_basic_ratio_calculation(self) -> None:
        """Test basic ratio calculation."""
        r1, r2 = compute_live_ratios(
            calories=500.0,
            cost=5.0,
            sodium_mcg=2_300_000.0,
            fat_g=15.0
        )
        assert r1 > 0
        assert r2 > 0

    def test_sodium_mcg_to_mg_conversion(self) -> None:
        """Verify sodium_mcg is converted to mg before ratio calc."""
        # With sodium_mcg=2_300_000 (2300 mg)
        r1_high_sodium, _ = compute_live_ratios(
            calories=500.0,
            cost=5.0,
            sodium_mcg=2_300_000.0,
            fat_g=15.0
        )
        # With sodium_mcg=230_000 (230 mg)
        r1_low_sodium, _ = compute_live_ratios(
            calories=500.0,
            cost=5.0,
            sodium_mcg=230_000.0,
            fat_g=15.0
        )
        # Higher sodium → lower ratio
        assert r1_high_sodium < r1_low_sodium

    def test_ratio2_includes_fat(self) -> None:
        """Verify ratio2 uses fat_g parameter."""
        r1_a, r2_a = compute_live_ratios(
            calories=500.0,
            cost=5.0,
            sodium_mcg=2_300_000.0,
            fat_g=5.0
        )
        r1_b, r2_b = compute_live_ratios(
            calories=500.0,
            cost=5.0,
            sodium_mcg=2_300_000.0,
            fat_g=25.0
        )
        # ratio1 unchanged by fat
        assert r1_a == r1_b
        # ratio2 differs by fat
        assert r2_a != r2_b
        assert r2_a > r2_b  # Higher fat → lower ratio2

    def test_zero_cost_sodium(self) -> None:
        """Test with zero cost and sodium (edge case)."""
        r1, r2 = compute_live_ratios(
            calories=500.0,
            cost=0.0,
            sodium_mcg=0.0,
            fat_g=10.0
        )
        assert r1 > 0
        assert r2 > 0

    def test_high_calorie_density(self) -> None:
        """Test high calorie-to-cost ratio."""
        r1_dense, r2_dense = compute_live_ratios(
            calories=1000.0,
            cost=2.0,
            sodium_mcg=1_000_000.0,
            fat_g=10.0
        )
        r1_sparse, r2_sparse = compute_live_ratios(
            calories=100.0,
            cost=10.0,
            sodium_mcg=1_000_000.0,
            fat_g=10.0
        )
        # Dense > sparse for both ratios
        assert r1_dense > r1_sparse
        assert r2_dense > r2_sparse
