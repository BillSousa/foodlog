from foodlog.calculations.ratios import ratio1, ratio2


def compute_live_ratios(
    calories: float, cost: float, sodium_mcg: float, fat_g: float
) -> tuple[float, float]:
    """Return (ratio1, ratio2) for a given set of aggregated totals.

    Parameters
    ----------
    calories : float
        Total calories across the aggregated set.
    cost : float
        Total cost in dollars across the aggregated set.
    sodium_mcg : float
        Total sodium in micrograms (raw aggregated total matching
        Item.sodium_mcg's storage unit). This function converts to
        milligrams before calling ratio1()/ratio2().
    fat_g : float
        Total fat in grams across the aggregated set.

    Returns
    -------
    tuple[float, float]
        (ratio1, ratio2) computed from the aggregated totals.
    """
    sodium_mg = sodium_mcg / 1000
    return ratio1(calories, cost, sodium_mg), ratio2(
        calories, cost, sodium_mg, fat_g
    )
