def dv_percent_to_mcg(percent: float, dv_amount_mcg: float) -> float:
    """
    Convert %DV (percent daily value) to mass in micrograms.

    Formula: mass_mcg = (percent / 100) * dv_amount_mcg

    Args:
        percent: %DV value from label (e.g., 50 for 50%)
        dv_amount_mcg: FDA daily value in micrograms

    Returns:
        float: Mass in micrograms
    """
    return (percent / 100) * dv_amount_mcg


def mcg_to_dv_percent(mass_mcg: float, dv_amount_mcg: float) -> float:
    """
    Convert mass in micrograms to %DV (percent daily value).

    Formula: percent = (mass_mcg / dv_amount_mcg) * 100

    Args:
        mass_mcg: Mass in micrograms
        dv_amount_mcg: FDA daily value in micrograms

    Returns:
        float: %DV value (e.g., 50 for 50%)
    """
    if dv_amount_mcg == 0:
        return 0.0
    return (mass_mcg / dv_amount_mcg) * 100
