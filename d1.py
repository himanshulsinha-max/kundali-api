from d1_whole_sign import build_d1_whole_sign


def calculate_d1(lagna_data, planets_data):
    """
    Build D1 Whole-Sign chart from already calculated
    Lagna and planetary positions.
    """

    ascendant_sign = lagna_data["sign"]

    return build_d1_whole_sign(
        ascendant_sign,
        planets_data
    )
