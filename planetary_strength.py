"""
Planetary Strength / Dignity Engine
-----------------------------------

Calculates classical Vedic planetary dignity and basic strength
from the already-calculated planetary positions.

This module does NOT calculate planetary longitude.
It consumes the output of planets.py.

Current scope:
- Exaltation
- Debilitation
- Own sign
- Moolatrikona
- Friendly sign
- Neutral sign
- Enemy sign
- Basic dignity score
- Combustion
- Retrograde status
- Overall dignity classification

Designed as a standalone engine.
Do not integrate into main.py until independently tested.
"""

from typing import Any, Dict


# -------------------------------------------------------------------
# PLANET DEFINITIONS
# -------------------------------------------------------------------

PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
]


# -------------------------------------------------------------------
# SIGN DEFINITIONS
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# PLANET LORDS
# -------------------------------------------------------------------

SIGN_LORDS = {
    0: "Mars",       # Aries
    1: "Venus",      # Taurus
    2: "Mercury",    # Gemini
    3: "Moon",       # Cancer
    4: "Sun",        # Leo
    5: "Mercury",    # Virgo
    6: "Venus",      # Libra
    7: "Mars",       # Scorpio
    8: "Jupiter",    # Sagittarius
    9: "Saturn",     # Capricorn
    10: "Saturn",    # Aquarius
    11: "Jupiter",   # Pisces
}


# -------------------------------------------------------------------
# EXALTATION
# Sign index + exact exaltation degree
# -------------------------------------------------------------------

EXALTATION = {
    "Sun": (0, 10.0),       # Aries 10°
    "Moon": (1, 3.0),       # Taurus 3°
    "Mars": (9, 28.0),      # Capricorn 28°
    "Mercury": (5, 15.0),   # Virgo 15°
    "Jupiter": (3, 5.0),    # Cancer 5°
    "Venus": (11, 27.0),    # Pisces 27°
    "Saturn": (6, 20.0),    # Libra 20°
}


# -------------------------------------------------------------------
# DEBILITATION
# -------------------------------------------------------------------

DEBILITATION = {
    "Sun": (6, 10.0),       # Libra 10°
    "Moon": (7, 3.0),       # Scorpio 3°
    "Mars": (3, 28.0),      # Cancer 28°
    "Mercury": (11, 15.0),  # Pisces 15°
    "Jupiter": (9, 5.0),    # Capricorn 5°
    "Venus": (5, 27.0),     # Virgo 27°
    "Saturn": (0, 20.0),    # Aries 20°
}


# -------------------------------------------------------------------
# MOOLATRIKONA
#
# Classical commonly-used ranges.
# -------------------------------------------------------------------

MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0),       # Leo 0°–20°
    "Moon": (1, 4.0, 30.0),      # Taurus 4°–30°
    "Mars": (0, 0.0, 12.0),      # Aries 0°–12°
    "Mercury": (5, 16.0, 20.0),  # Virgo 16°–20°
    "Jupiter": (8, 0.0, 10.0),   # Sagittarius 0°–10°
    "Venus": (6, 0.0, 15.0),    # Libra 0°–15°
    "Saturn": (10, 0.0, 20.0),   # Aquarius 0°–20°
}


# -------------------------------------------------------------------
# OWN SIGNS
# -------------------------------------------------------------------

OWN_SIGNS = {
    "Sun": [4],                 # Leo
    "Moon": [3],                # Cancer
    "Mars": [0, 7],             # Aries, Scorpio
    "Mercury": [2, 5],          # Gemini, Virgo
    "Jupiter": [8, 11],         # Sagittarius, Pisces
    "Venus": [1, 6],            # Taurus, Libra
    "Saturn": [9, 10],          # Capricorn, Aquarius
}


# -------------------------------------------------------------------
# NATURAL FRIENDSHIP
#
# Classical natural relationship table.
# -------------------------------------------------------------------

NATURAL_RELATIONSHIPS = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "enemies": ["Venus", "Saturn"],
        "neutral": ["Mercury"],
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "enemies": [],
        "neutral": ["Mars", "Jupiter", "Venus", "Saturn"],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "enemies": ["Mercury"],
        "neutral": ["Venus", "Saturn"],
    },
    "Mercury": {
        "friends": ["Sun", "Venus"],
        "enemies": ["Moon"],
        "neutral": ["Mars", "Jupiter", "Saturn"],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "enemies": ["Mercury", "Venus"],
        "neutral": ["Saturn"],
    },
    "Venus": {
        "friends": ["Mercury", "Saturn"],
        "enemies": ["Sun", "Moon"],
        "neutral": ["Mars", "Jupiter"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutral": ["Jupiter"],
    },
}


# -------------------------------------------------------------------
# DIGNITY SCORES
#
# These are ENGINE classification scores, not Shadbala.
# Do not confuse this with the later Shadbala module.
# -------------------------------------------------------------------

DIGNITY_SCORES = {
    "exalted": 5,
    "moolatrikona": 4,
    "own_sign": 3,
    "friendly_sign": 2,
    "neutral_sign": 1,
    "enemy_sign": -1,
    "debilitated": -4,
}


# -------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------

def normalize_degree(degree: float) -> float:
    """Keep degree inside 0°–30°."""
    return max(0.0, min(float(degree), 29.999999))


def get_sign_index(planet_data: Dict[str, Any]) -> int:
    """
    Extract sign index from planets.py output.
    """
    if "sign_index" in planet_data:
        return int(planet_data["sign_index"])

    sign = planet_data.get("sign")

    if isinstance(sign, str):
        if sign in SIGNS:
            return SIGNS.index(sign)

        # Handle common capitalization differences
        normalized = sign.strip().capitalize()

        if normalized in SIGNS:
            return SIGNS.index(normalized)

    raise ValueError(
        "Planet data must contain a valid 'sign_index' or 'sign'."
    )


def get_degree_in_sign(planet_data: Dict[str, Any]) -> float:
    """
    Extract degree within the sign from planets.py output.
    """

    if "degree_in_sign" in planet_data:
        return normalize_degree(planet_data["degree_in_sign"])

    dms = planet_data.get("degree_dms")

    if isinstance(dms, dict):
        degrees = float(dms.get("degrees", 0))
        minutes = float(dms.get("minutes", 0))
        seconds = float(dms.get("seconds", 0))

        return normalize_degree(
            degrees + (minutes / 60.0) + (seconds / 3600.0)
        )

    raise ValueError(
        "Planet data must contain 'degree_in_sign' "
        "or 'degree_dms'."
    )


def get_sign_name(sign_index: int) -> str:
    """Return sign name from index."""
    if sign_index < 0 or sign_index > 11:
        raise ValueError("sign_index must be between 0 and 11.")

    return SIGNS[sign_index]


def get_sign_lord(sign_index: int) -> str:
    """Return lord of a zodiac sign."""
    if sign_index not in SIGN_LORDS:
        raise ValueError("Invalid sign index.")

    return SIGN_LORDS[sign_index]


# -------------------------------------------------------------------
# DIGNITY CALCULATION
# -------------------------------------------------------------------

def calculate_dignity(
    planet: str,
    sign_index: int,
    degree_in_sign: float,
) -> Dict[str, Any]:
    """
    Calculate classical planetary dignity.
    """

    if planet not in PLANETS:
        raise ValueError(f"Unsupported planet: {planet}")

    degree_in_sign = normalize_degree(degree_in_sign)

    sign_name = get_sign_name(sign_index)
    sign_lord = get_sign_lord(sign_index)

    dignity = "neutral_sign"
    score = DIGNITY_SCORES["neutral_sign"]

    # ---------------------------------------------------------------
    # Exaltation
    # ---------------------------------------------------------------

    exalt_sign, exalt_degree = EXALTATION[planet]

    if sign_index == exalt_sign:
        if abs(degree_in_sign - exalt_degree) < 0.0001:
            dignity = "exalted"
            score = DIGNITY_SCORES["exalted"]

    # ---------------------------------------------------------------
    # Debilitation
    # ---------------------------------------------------------------

    debil_sign, debil_degree = DEBILITATION[planet]

    if sign_index == debil_sign:
        if abs(degree_in_sign - debil_degree) < 0.0001:
            dignity = "debilitated"
            score = DIGNITY_SCORES["debilitated"]

    # ---------------------------------------------------------------
    # Moolatrikona
    # ---------------------------------------------------------------

    mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]

    if (
        sign_index == mt_sign
        and mt_start <= degree_in_sign <= mt_end
    ):
        dignity = "moolatrikona"
        score = DIGNITY_SCORES["moolatrikona"]

    # ---------------------------------------------------------------
    # Own sign
    # ---------------------------------------------------------------

    if sign_index in OWN_SIGNS[planet]:
        dignity = "own_sign"
        score = DIGNITY_SCORES["own_sign"]

    # ---------------------------------------------------------------
    # Natural relationship with sign lord
    # ---------------------------------------------------------------

    if sign_lord == planet:
        dignity = "own_sign"
        score = DIGNITY_SCORES["own_sign"]

    elif sign_lord in NATURAL_RELATIONSHIPS[planet]["friends"]:
        dignity = "friendly_sign"
        score = DIGNITY_SCORES["friendly_sign"]

    elif sign_lord in NATURAL_RELATIONSHIPS[planet]["enemies"]:
        dignity = "enemy_sign"
        score = DIGNITY_SCORES["enemy_sign"]

    elif sign_lord in NATURAL_RELATIONSHIPS[planet]["neutral"]:
        dignity = "neutral_sign"
        score = DIGNITY_SCORES["neutral_sign"]

    return {
        "planet": planet,
        "sign": sign_name,
        "sign_index": sign_index,
        "degree_in_sign": round(degree_in_sign, 6),
        "sign_lord": sign_lord,
        "dignity": dignity,
        "dignity_score": score,
        "exaltation_degree": exalt_degree,
        "debilitation_degree": debil_degree,
    }


# -------------------------------------------------------------------
# COMBUSTION
# -------------------------------------------------------------------

COMBUSTION_LIMITS = {
    "Moon": None,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}


def angular_distance(longitude1: float, longitude2: float) -> float:
    """
    Calculate smallest angular distance between two longitudes.
    """

    difference = abs(longitude1 - longitude2) % 360.0

    return min(difference, 360.0 - difference)


def calculate_combustion(
    planet: str,
    planet_data: Dict[str, Any],
    sun_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate basic combustion using angular distance from Sun.

    Note:
    Traditional combustion rules have school-specific variations.
    This engine keeps the threshold explicit and configurable.
    """

    if planet == "Sun":
        return {
            "combust": False,
            "distance_from_sun": 0.0,
            "combustion_limit": None,
        }

    limit = COMBUSTION_LIMITS.get(planet)

    if limit is None:
        return {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": None,
        }

    if "longitude" not in planet_data:
        return {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": limit,
            "status": "longitude_not_available",
        }

    if "longitude" not in sun_data:
        return {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": limit,
            "status": "sun_longitude_not_available",
        }

    distance = angular_distance(
        float(planet_data["longitude"]),
        float(sun_data["longitude"]),
    )

    return {
        "combust": distance <= limit,
        "distance_from_sun": round(distance, 6),
        "combustion_limit": limit,
    }


# -------------------------------------------------------------------
# SINGLE PLANET STRENGTH
# -------------------------------------------------------------------

def calculate_planetary_strength(
    planet: str,
    planet_data: Dict[str, Any],
    sun_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Calculate dignity and basic strength information
    for one planet.
    """

    sign_index = get_sign_index(planet_data)
    degree_in_sign = get_degree_in_sign(planet_data)

    dignity = calculate_dignity(
        planet=planet,
        sign_index=sign_index,
        degree_in_sign=degree_in_sign,
    )

    retrograde = bool(planet_data.get("retrograde", False))

    result = {
        **dignity,
        "retrograde": retrograde,
        "combustion": {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": None,
        },
    }

    if sun_data is not None and planet != "Sun":
        result["combustion"] = calculate_combustion(
            planet=planet,
            planet_data=planet_data,
            sun_data=sun_data,
        )

    return result


# -------------------------------------------------------------------
# ALL PLANETS
# -------------------------------------------------------------------

def calculate_planetary_strengths(
    planets_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate planetary strength/dignity for all supported planets.

    Expected input:

    {
        "Sun": {...},
        "Moon": {...},
        "Mars": {...},
        ...
    }
    """

    results = {}

    sun_data = planets_data.get("Sun")

    for planet in PLANETS:

        if planet not in planets_data:
            continue

        results[planet] = calculate_planetary_strength(
            planet=planet,
            planet_data=planets_data[planet],
            sun_data=sun_data,
        )

    return results


# -------------------------------------------------------------------
# PUBLIC API ALIAS
# -------------------------------------------------------------------

def calculate_strength(
    planets_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Public API alias.

    Keeps the module easy to integrate into main.py later.
    """

    return calculate_planetary_strengths(planets_data)
