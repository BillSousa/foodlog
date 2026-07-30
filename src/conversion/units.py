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
