# house_lords.py

from d1_whole_sign import SIGNS, sign_for_house


# Vedic planetary rulership
SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


def get_sign_lord(sign):
    """
    Return the classical Vedic lord of a zodiac sign.
    """

    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGN_LORDS:
        raise ValueError(f"Invalid zodiac sign: {sign}")

    return SIGN_LORDS[sign]


def get_house_lord(ascendant_sign, house_number):
    """
    Return the lord of a Whole-Sign house.
    """

    house_sign = sign_for_house(
        ascendant_sign,
        house_number
    )

    lord = get_sign_lord(house_sign)

    return {
        "house": house_number,
        "sign": house_sign,
        "lord": lord,
    }


def build_house_lords(ascendant_sign):
    """
    Build lords for all 12 D1 houses.
    """

    result = {}

    for house_number in range(1, 13):

        result[house_number] = get_house_lord(
            ascendant_sign,
            house_number
        )

    return result
