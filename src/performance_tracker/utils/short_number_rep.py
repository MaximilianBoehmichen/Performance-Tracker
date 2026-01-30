TEN = 10
HUNDRED = 100


def short_rep(number: int | float | str | None) -> str:
    if number is None or number == "":
        return ""
    try:
        num = float(number)
    except (ValueError, TypeError):
        return ""

    if num == 0:
        return "0.00"

    return _unit_short_rep(num)


def _unit_short_rep(num: float) -> str:
    sign = "-" if num < 0 else ""
    num = abs(num)

    units = [(1e15, "INF"), (1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k"), (1e0, "")]

    for threshold, unit in units:
        if num >= threshold:
            if unit == "INF":
                return f"{sign}INF"

            val = num / threshold
            if val < TEN:
                return f"{sign}{val:.2f}{unit}"
            if val < HUNDRED:
                return f"{sign}{val:.1f}{unit}"
            return f"{sign}{val:.0f}{unit}"

    return f"{sign}{num:.2f}"
