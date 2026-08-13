def to_negative(value: float) -> float:
    """Force a value negative regardless of the sign entered.

    Parameters
    ----------
    value : float
        User-entered amount, any sign.

    Returns
    -------
    float
        The value made negative (0 stays 0).
    """
    return -abs(value)
