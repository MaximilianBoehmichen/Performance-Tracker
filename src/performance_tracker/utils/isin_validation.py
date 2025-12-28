import sys
from typing import Dict, List, Union

import yfinance as yf


def isin_to_digits(isin_like: str) -> str:
    result = ""

    for character in isin_like.upper():
        if character.isdigit():
            result += character
        elif character.isalpha():
            result += str(ord(character) - 55)
        else:
            raise ValueError(f"Invalid character in ISIN: {isin_like}")

    return result


def luhn_checksum(isin_like: str) -> bool:
    total = 0
    reverse_digits = isin_like[::-1]

    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0


def validate(isin: Union[str, List[str]]) -> Union[bool, Dict[str, bool]]:
    """
    validates given isins to be correctly formatted
    :param isin: isins to be validated
    :return: correctness of isins
    """

    def _validate(single_isin: str) -> bool:
        if not yf.utils.is_isin(single_isin):
            return False

        try:
            digits = isin_to_digits(single_isin)
        except ValueError as e:
            sys.stderr.write(f"{e}\n")
            return False
        return luhn_checksum(digits)

    if isinstance(isin, str):
        return _validate(isin)
    elif isinstance(isin, list):
        return {_isin: _validate(_isin) for _isin in isin}
    else:
        raise TypeError("isin must be str or list")


if __name__ == "__main__":
    print(validate("DE000BAY0017"))
