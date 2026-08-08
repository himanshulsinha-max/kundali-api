# house_lords.py

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


SIGN_INDEX = {
    sign: index
    for index, sign in enumerate(SIGNS)
}


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


def normalize_sign(sign):

    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGN_INDEX:
        raise ValueError(
            f"Invalid zodiac sign: {sign}"
        )

    return sign


def sign_for_house(ascendant_sign, house_number):

    ascendant_sign = normalize_sign(
        ascendant_sign
    )

    if not isinstance(house_number, int):
        raise TypeError(
            "House number must be an integer."
        )

    if not 1 <= house_number <= 12:
        raise ValueError(
            "House number must be between 1 and 12."
        )

    asc_index = SIGN_INDEX[ascendant_sign]

    return SIGNS[
        (asc_index + house_number - 1) % 12
    ]


def get_sign_lord(sign):

    sign = normalize_sign(sign)

    return SIGN_LORDS[sign]


def get_house_lord(ascendant_sign, house_number):

    house_sign = sign_for_house(
        ascendant_sign,
        house_number
    )

    lord = get_sign_lord(
        house_sign
    )

    return {
        "house": house_number,
        "sign": house_sign,
        "lord": lord,
    }


def build_house_lords(ascendant_sign):

    result = {}

    for house_number in range(1, 13):

        result[house_number] = get_house_lord(
            ascendant_sign,
            house_number
        )

    return result
