# planet_strength.py

from planets import SIGNS


PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
]


# ---------------------------------------------------------
# EXALTATION
# ---------------------------------------------------------
# Sign + exact exaltation degree
# ---------------------------------------------------------

EXALTATION = {
    "Sun": ("Aries", 10.0),
    "Moon": ("Taurus", 3.0),
    "Mars": ("Capricorn", 28.0),
    "Mercury": ("Virgo", 15.0),
    "Jupiter": ("Cancer", 5.0),
    "Venus": ("Pisces", 27.0),
    "Saturn": ("Libra", 20.0),
}


# ---------------------------------------------------------
# DEBILITATION
# ---------------------------------------------------------

DEBILITATION = {
    "Sun": ("Libra", 10.0),
    "Moon": ("Scorpio", 3.0),
    "Mars": ("Cancer", 28.0),
    "Mercury": ("Pisces", 15.0),
    "Jupiter": ("Capricorn", 5.0),
    "Venus": ("Virgo", 27.0),
    "Saturn": ("Aries", 20.0),
}


# ---------------------------------------------------------
# OWN SIGNS
# ---------------------------------------------------------

OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
}


# ---------------------------------------------------------
# MOOLATRIKONA
# ---------------------------------------------------------
#
# Stored as:
#     planet: (sign, start_degree, end_degree)
#
# Degrees are measured within the sign.
# ---------------------------------------------------------

MOOLATRIKONA = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 4.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 16.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}


# ---------------------------------------------------------
# NATURAL FRIENDSHIP
# ---------------------------------------------------------

NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}


NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}


def normalize_planet(planet):
    if not isinstance(planet, str):
        raise TypeError("Planet must be a string.")

    planet = planet.strip().title()

    if planet not in PLANETS:
        raise ValueError(
            f"Unsupported planet for dignity: {planet}"
        )

    return planet


def normalize_sign(sign):
    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGNS:
        raise ValueError(
            f"Invalid zodiac sign: {sign}"
        )

    return sign


def get_exaltation_status(
    planet,
    sign,
    degree_in_sign
):
    """
    Determine whether planet is exalted,
    debilitated, or neither.
    """

    planet = normalize_planet(planet)
    sign = normalize_sign(sign)

    exalted_sign, exalted_degree = EXALTATION[planet]
    debilitated_sign, debilitated_degree = DEBILITATION[planet]

    if sign == exalted_sign:
        return "exalted"

    if sign == debilitated_sign:
        return "debilitated"

    return None


def is_moolatrikona(
    planet,
    sign,
    degree_in_sign
):
    """
    Check whether the planet lies inside
    its defined Moolatrikona range.
    """

    planet = normalize_planet(planet)
    sign = normalize_sign(sign)

    mt_sign, start_degree, end_degree = (
        MOOLATRIKONA[planet]
    )

    if sign != mt_sign:
        return False

    return (
        start_degree
        <= degree_in_sign
        <= end_degree
    )


def is_own_sign(planet, sign):
    """
    Check whether planet is in one of its own signs.
    """

    planet = normalize_planet(planet)
    sign = normalize_sign(sign)

    return sign in OWN_SIGNS[planet]


def get_natural_relationship(
    planet,
    sign_lord
):
    """
    Determine planet's natural relationship
    with the lord of its current sign.
    """

    planet = normalize_planet(planet)
    sign_lord = normalize_planet(sign_lord)

    if sign_lord == planet:
        return "own"

    if sign_lord in NATURAL_FRIENDS[planet]:
        return "friend"

    if sign_lord in NATURAL_ENEMIES[planet]:
        return "enemy"

    return "neutral"


def get_sign_lord(sign):
    """
    Return classical sign lord.
    """

    sign = normalize_sign(sign)

    sign_lords = {
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

    return sign_lords[sign]


def get_dignity(
    planet,
    sign,
    degree_in_sign
):
    """
    Determine the primary sign dignity of a planet.
    """

    planet = normalize_planet(planet)
    sign = normalize_sign(sign)

    exaltation = get_exaltation_status(
        planet,
        sign,
        degree_in_sign
    )

    moolatrikona = is_moolatrikona(
        planet,
        sign,
        degree_in_sign
    )

    own_sign = is_own_sign(
        planet,
        sign
    )

    sign_lord = get_sign_lord(sign)

    relationship = get_natural_relationship(
        planet,
        sign_lord
    )

    if exaltation == "exalted":
        dignity = "exalted"

    elif exaltation == "debilitated":
        dignity = "debilitated"

    elif moolatrikona:
        dignity = "moolatrikona"

    elif own_sign:
        dignity = "own_sign"

    elif relationship == "friend":
        dignity = "friend_sign"

    elif relationship == "enemy":
        dignity = "enemy_sign"

    else:
        dignity = "neutral_sign"

    return {
        "planet": planet,
        "sign": sign,
        "degree_in_sign": round(
            degree_in_sign,
            8
        ),
        "sign_lord": sign_lord,
        "natural_relationship": relationship,
        "dignity": dignity,
        "exalted": exaltation == "exalted",
        "debilitated": exaltation == "debilitated",
        "moolatrikona": moolatrikona,
        "own_sign": own_sign,
    }


def build_planet_dignities(planets):
    """
    Build dignity information for all supported
    visible planets.

    Rahu/Ketu are deliberately excluded from
    classical seven-planet sign dignity here.
    """

    result = {}

    for planet, data in planets.items():

        if planet not in PLANETS:
            continue

        if not isinstance(data, dict):
            raise TypeError(
                f"Invalid data for {planet}"
            )

        sign = data.get("sign")
        degree = data.get("degree_in_sign")

        if sign is None:
            raise ValueError(
                f"Missing sign for {planet}"
            )

        if degree is None:
            raise ValueError(
                f"Missing degree_in_sign for {planet}"
            )

        result[planet] = get_dignity(
            planet,
            sign,
            degree
        )

    return result
