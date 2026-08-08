# d1.py

from d1_whole_sign import build_d1_whole_sign


def build_d1_chart(lagna_data, planet_data):
    """
    Build D1 chart using already-calculated
    Lagna and planetary positions.
    """

    ascendant_sign = lagna_data["sign"]

    return build_d1_whole_sign(
        ascendant_sign,
        planet_data
    )
