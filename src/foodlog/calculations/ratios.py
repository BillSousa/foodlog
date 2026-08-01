def ratio1(calories: float, cost: float, sodium_mg: float) -> float:
    """
    Ratio1 = Calories / (4 × Cost + Sodium_mg/100 + 0.00001).

    Higher is better. Primary efficiency metric.

    Args:
        calories: Total calories
        cost: Total cost in dollars
        sodium_mg: Total sodium in milligrams

    Returns:
        float: Ratio1 score
    """
    denominator = (4 * cost) + (sodium_mg / 100) + 0.00001
    return calories / denominator


def ratio2(calories: float, cost: float, sodium_mg: float,
           fat_g: float) -> float:
    """
    Ratio2 = Calories / (1.333 × Cost + Sodium_mg/300 + Fat_g/6.6 + 0.00001).

    Higher is better. Secondary efficiency metric (includes fat trade-off).

    Args:
        calories: Total calories
        cost: Total cost in dollars
        sodium_mg: Total sodium in milligrams
        fat_g: Total fat in grams

    Returns:
        float: Ratio2 score
    """
    denominator = (1.333 * cost) + (sodium_mg / 300) + (fat_g / 6.6) + 0.00001
    return calories / denominator
