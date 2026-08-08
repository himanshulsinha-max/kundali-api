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

SIGN_INDEX = {sign: i for i, sign in enumerate(SIGNS)}


def normalize_sign(sign):
    if not isinstance(sign, str):
        raise TypeError("Zodiac sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGN_INDEX:
        raise ValueError(f"Invalid zodiac sign: {sign}")

    return sign


def house_from_sign(ascendant_sign, planet_sign):
    """
    D1 Whole-Sign house calculation.

    Ascendant sign = 1st house.
    Each subsequent zodiac sign = next house.
    """

    ascendant_sign = normalize_sign(ascendant_sign)
    planet_sign = normalize_sign(planet_sign)

    asc_index = SIGN_INDEX[ascendant_sign]
    planet_index = SIGN_INDEX[planet_sign]

    return ((planet_index - asc_index) % 12) + 1


def sign_for_house(ascendant_sign, house_number):
    """
    Return the zodiac sign occupying a Whole-Sign house.
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    if not isinstance(house_number, int):
        raise TypeError("House number must be an integer.")

    if not 1 <= house_number <= 12:
        raise ValueError("House number must be between 1 and 12.")

    asc_index = SIGN_INDEX[ascendant_sign]

    return SIGNS[(asc_index + house_number - 1) % 12]


def build_houses(ascendant_sign):
    """
    Create the complete 12-house D1 Whole-Sign structure.
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
            "planets": [],
        }

    return houses


def map_planets_to_houses(ascendant_sign, planets):
    """
    Map planets to houses.

    Expected input:

    {
        "Sun": {"sign": "Leo"},
        "Moon": {"sign": "Virgo"}
    }
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    mapping = {}

    for planet, planet_data in planets.items():

        if not isinstance(planet_data, dict):
            raise TypeError(
                f"Invalid data for planet: {planet}"
            )

        planet_sign = planet_data.get("sign")

        if planet_sign is None:
            raise ValueError(
                f"Missing sign for planet: {planet}"
            )

        mapping[planet] = house_from_sign(
            ascendant_sign,
            planet_sign
        )

    return mapping


def build_d1_whole_sign(ascendant_sign, planets):
    """
    Build complete D1 Whole-Sign chart.
    """

    ascendant_sign = normalize_sign(ascendant_sign)

    houses = build_houses(ascendant_sign)

    planet_house_mapping = map_planets_to_houses(
        ascendant_sign,
        planets
    )

    for planet, house_number in planet_house_mapping.items():
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
