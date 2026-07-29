from src.calculations.ratios import ratio1, ratio2


def test_ratio1_basic() -> None:
    """Test Ratio1 calculation."""
    result = ratio1(calories=1000, cost=5.0, sodium_mg=2000)
    assert result > 0
    assert isinstance(result, float)


def test_ratio1_higher_cost_lower_ratio() -> None:
    """Test Ratio1 decreases with cost."""
    r1 = ratio1(calories=1000, cost=5.0, sodium_mg=0)
    r2 = ratio1(calories=1000, cost=10.0, sodium_mg=0)
    assert r1 > r2


def test_ratio2_basic() -> None:
    """Test Ratio2 calculation."""
    result = ratio2(calories=1000, cost=5.0, sodium_mg=2000, fat_g=10)
    assert result > 0
    assert isinstance(result, float)


def test_ratio2_includes_fat() -> None:
    """Test Ratio2 decreases with fat."""
    r1 = ratio2(calories=1000, cost=5.0, sodium_mg=0, fat_g=0)
    r2 = ratio2(calories=1000, cost=5.0, sodium_mg=0, fat_g=20)
    assert r1 > r2
