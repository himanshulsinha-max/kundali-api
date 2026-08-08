# d1_whole_sign.py

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

SIGN_INDEX = {sign: index for index, sign in enumerate(SIGNS)}


def normalize_sign(sign):
    """
    Normalize a zodiac sign name.

    Example:
        'aries' -> 'Aries'
        'ARIES' -> 'Aries'
    """
    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    normalized = sign.strip().title()

    if normalized not in SIGN_INDEX:
        raise ValueError(f"Invalid zodiac sign: {sign}")

    return normalized


def house_from_sign(ascendant_sign, planet_sign):
    """
    Calculate Whole-Sign house number.

    Ascendant sign = House 1.
    Each following zodiac sign advances one house.
    """

    ascendant_sign = normalize_sign(ascendant_sign)
    planet_sign = normalize_sign(planet_sign)

    asc_index = SIGN_INDEX[ascendant_sign]
    planet_index = SIGN_INDEX[planet_sign]

    house = ((planet_index - asc_index) % 12) + 1

    return house


def sign_for_house(ascendant_sign, house_number):
    """
    Return the zodiac sign occupying a given Whole-Sign house.
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    if not isinstance(house_number, int):
        raise TypeError("House number must be an integer.")

    if house_number < 1 or house_number > 12:
        raise ValueError("House number must be between 1 and 12.")

    asc_index = SIGN_INDEX[ascendant_sign]

    sign_index = (asc_index + house_number - 1) % 12

    return SIGNS[sign_index]


def build_whole_sign_houses(ascendant_sign):
    """
    Build all 12 D1 Whole-Sign houses.
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    houses = {}

    for house_number in range(1, 13):
        houses[house_number] = {
            "house": house_number,
            "sign": sign_for_house(
                ascendant_sign,
                house_number
            ),
        }

    return houses


def map_planets_to_houses(ascendant_sign, planets):
    """
    Map planets to Whole-Sign houses.

    Expected planet structure:

    {
        "Sun": {"sign": "Leo"},
        "Moon": {"sign": "Virgo"}
    }

    Returns:

    {
        "Sun": 1,
        "Moon": 2
    }
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    if not isinstance(planets, dict):
        raise TypeError("Planets must be a dictionary.")

    mapping = {}

    for planet, data in planets.items():

        if not isinstance(data, dict):
            raise TypeError(
                f"Planet data for {planet} must be a dictionary."
            )

        if "sign" not in data:
            raise ValueError(
                f"Missing 'sign' for planet: {planet}"
            )

        planet_sign = normalize_sign(data["sign"])

        mapping[planet] = house_from_sign(
            ascendant_sign,
            planet_sign
        )

    return mapping


def build_d1_whole_sign(ascendant_sign, planets):
    """
    Build the complete D1 Whole-Sign structure.
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    houses = build_whole_sign_houses(ascendant_sign)

    planet_house_mapping = map_planets_to_houses(
        ascendant_sign,
        planets
    )

    # Add planets inside their respective houses
    for planet, house_number in planet_house_mapping.items():

        houses[house_number].setdefault("planets", [])

        houses[house_number]["planets"].append(planet)

    return {
        "chart": "D1",
        "house_system": "whole_sign",
        "ascendant": {
            "sign": ascendant_sign
        },
        "houses": houses,
        "planet_house_mapping": planet_house_mapping,
    }
