from foodlog.calculations.ratios import ratio1, ratio2


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


def test_ratio1_cost_coefficient_is_4() -> None:
    """Verify Ratio1 cost multiplier is exactly 4."""
    # Ratio1 = 1000 / (4*2.5 + 0/100 + 0.00001)
    # = 1000 / 10.00001 ≈ 99.9999
    result = ratio1(calories=1000, cost=2.5, sodium_mg=0)
    expected = 1000 / (4 * 2.5 + 0.00001)
    assert abs(result - expected) < 1e-10


def test_ratio1_sodium_divisor_is_100() -> None:
    """Verify Ratio1 sodium divisor is exactly 100."""
    # Ratio1 = 1000 / (4*1 + 2000/100 + 0.00001)
    # = 1000 / (4 + 20 + 0.00001) = 1000 / 24.00001
    result = ratio1(calories=1000, cost=1.0, sodium_mg=2000)
    expected = 1000 / (4 * 1.0 + 2000 / 100 + 0.00001)
    assert abs(result - expected) < 1e-10


def test_ratio1_epsilon_prevents_divide_by_zero() -> None:
    """Verify Ratio1 epsilon (0.00001) prevents division by zero."""
    # With cost=0, sodium_mg=0, epsilon should dominate denominator
    result = ratio1(calories=1000, cost=0, sodium_mg=0)
    expected = 1000 / 0.00001
    assert abs(result - expected) < 1e-10


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


def test_ratio2_cost_coefficient_is_1_333() -> None:
    """Verify Ratio2 cost multiplier is exactly 1.333."""
    # Ratio2 = 1000 / (1.333*3 + 0/300 + 0/6.6 + 0.00001)
    # = 1000 / (3.999 + 0.00001)
    result = ratio2(calories=1000, cost=3.0, sodium_mg=0, fat_g=0)
    expected = 1000 / (1.333 * 3.0 + 0.00001)
    assert abs(result - expected) < 1e-10


def test_ratio2_sodium_divisor_is_300() -> None:
    """Verify Ratio2 sodium divisor is exactly 300."""
    # Ratio2 = 1000 / (1.333*1 + 3000/300 + 0/6.6 + 0.00001)
    # = 1000 / (1.333 + 10 + 0.00001)
    result = ratio2(calories=1000, cost=1.0, sodium_mg=3000, fat_g=0)
    expected = 1000 / (1.333 * 1.0 + 3000 / 300 + 0.00001)
    assert abs(result - expected) < 1e-10


def test_ratio2_fat_divisor_is_6_6() -> None:
    """Verify Ratio2 fat divisor is exactly 6.6."""
    # Ratio2 = 1000 / (1.333*1 + 0/300 + 33/6.6 + 0.00001)
    # = 1000 / (1.333 + 5 + 0.00001)
    result = ratio2(calories=1000, cost=1.0, sodium_mg=0, fat_g=33)
    expected = 1000 / (1.333 * 1.0 + 33 / 6.6 + 0.00001)
    assert abs(result - expected) < 1e-10


def test_ratio2_epsilon_prevents_divide_by_zero() -> None:
    """Verify Ratio2 epsilon (0.00001) prevents division by zero."""
    # With all inputs zero, epsilon should dominate denominator
    result = ratio2(calories=1000, cost=0, sodium_mg=0, fat_g=0)
    expected = 1000 / 0.00001
    assert abs(result - expected) < 1e-10


def test_ratio1_mcg_conversion_bug_caught() -> None:
    """Catch a caller who forgets mcg→mg conversion.

    If a caller passes raw sodium_mcg (e.g., 2_300_000 mcg instead of
    2_300 mg), the result will be drastically wrong. This test proves
    the bug is detectable.
    """
    # Correct: 2_300 mg sodium
    correct = ratio1(calories=1000, cost=5.0, sodium_mg=2_300)

    # Wrong: forgot to convert, passed 2_300_000 (as if it were mg)
    wrong = ratio1(calories=1000, cost=5.0, sodium_mg=2_300_000)

    # Wrong result should be much smaller (larger denominator)
    assert wrong < correct / 10


def test_ratio2_mcg_conversion_bug_caught() -> None:
    """Catch a caller who forgets mcg→mg conversion in Ratio2.

    If a caller passes raw sodium_mcg (e.g., 2_300_000 mcg instead of
    2_300 mg), the result will be drastically wrong. This test proves
    the bug is detectable.
    """
    # Correct: 2_300 mg sodium
    correct = ratio2(calories=1000, cost=5.0, sodium_mg=2_300, fat_g=10)

    # Wrong: forgot to convert, passed 2_300_000 (as if it were mg)
    wrong = ratio2(calories=1000, cost=5.0, sodium_mg=2_300_000, fat_g=10)

    # Wrong result should be much smaller (larger denominator)
    assert wrong < correct / 10
