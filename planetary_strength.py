"""
Planetary Strength / Dignity Engine
-----------------------------------

Calculates classical Vedic planetary dignity and basic strength
from the planetary positions already calculated by planets.py.

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
- Deep exaltation / debilitation degree markers
- Combustion
- Retrograde status

This is NOT Shadbala.
Shadbala will be implemented as a separate engine.
"""

from typing import Any, Dict, Optional


PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
]


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


SIGN_LORDS = {
    0: "Mars",
    1: "Venus",
    2: "Mercury",
    3: "Moon",
    4: "Sun",
    5: "Mercury",
    6: "Venus",
    7: "Mars",
    8: "Jupiter",
    9: "Saturn",
    10: "Saturn",
    11: "Jupiter",
}


# Planet: (sign index, deepest exaltation degree)
EXALTATION = {
    "Sun": (0, 10.0),
    "Moon": (1, 3.0),
    "Mars": (9, 28.0),
    "Mercury": (5, 15.0),
    "Jupiter": (3, 5.0),
    "Venus": (11, 27.0),
    "Saturn": (6, 20.0),
}


# Planet: (sign index, deepest debilitation degree)
DEBILITATION = {
    "Sun": (6, 10.0),
    "Moon": (7, 3.0),
    "Mars": (3, 28.0),
    "Mercury": (11, 15.0),
    "Jupiter": (9, 5.0),
    "Venus": (5, 27.0),
    "Saturn": (0, 20.0),
}


# Planet: (sign index, start degree, end degree)
MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0),
    "Moon": (1, 4.0, 30.0),
    "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 16.0, 20.0),
    "Jupiter": (8, 0.0, 10.0),
    "Venus": (6, 0.0, 15.0),
    "Saturn": (10, 0.0, 20.0),
}


OWN_SIGNS = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
}


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


DIGNITY_SCORES = {
    "exalted": 5,
    "moolatrikona": 4,
    "own_sign": 3,
    "friendly_sign": 2,
    "neutral_sign": 1,
    "enemy_sign": -1,
    "debilitated": -4,
}


COMBUSTION_LIMITS = {
    "Moon": None,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}


def normalize_degree(degree: float) -> float:
    """Keep degree inside 0 <= degree < 30."""
    return max(0.0, min(float(degree), 29.999999))


def get_sign_index(planet_data: Dict[str, Any]) -> int:
    """Extract sign index from planets.py output."""
    if "sign_index" in planet_data:
        sign_index = int(planet_data["sign_index"])
        if 0 <= sign_index <= 11:
            return sign_index
        raise ValueError("sign_index must be between 0 and 11.")

    sign = planet_data.get("sign")

    if isinstance(sign, str):
        normalized = sign.strip().capitalize()
        if normalized in SIGNS:
            return SIGNS.index(normalized)

    raise ValueError(
        "Planet data must contain a valid 'sign_index' or 'sign'."
    )


def get_degree_in_sign(planet_data: Dict[str, Any]) -> float:
    """Extract degree within the sign from planets.py output."""
    if "degree_in_sign" in planet_data:
        return normalize_degree(planet_data["degree_in_sign"])

    dms = planet_data.get("degree_dms")

    if isinstance(dms, dict):
        degrees = float(dms.get("degrees", 0))
        minutes = float(dms.get("minutes", 0))
        seconds = float(dms.get("seconds", 0))

        return normalize_degree(
            degrees + minutes / 60.0 + seconds / 3600.0
        )

    raise ValueError(
        "Planet data must contain 'degree_in_sign' or 'degree_dms'."
    )


def get_sign_name(sign_index: int) -> str:
    """Return sign name from sign index."""
    if sign_index < 0 or sign_index > 11:
        raise ValueError("sign_index must be between 0 and 11.")
    return SIGNS[sign_index]


def get_sign_lord(sign_index: int) -> str:
    """Return the classical lord of a zodiac sign."""
    if sign_index not in SIGN_LORDS:
        raise ValueError("Invalid sign index.")
    return SIGN_LORDS[sign_index]


def calculate_dignity(
    planet: str,
    sign_index: int,
    degree_in_sign: float,
) -> Dict[str, Any]:
    """Calculate classical planetary dignity."""
    if planet not in PLANETS:
        raise ValueError(f"Unsupported planet: {planet}")

    if not 0 <= sign_index <= 11:
        raise ValueError("sign_index must be between 0 and 11.")

    degree_in_sign = normalize_degree(degree_in_sign)
    sign_name = get_sign_name(sign_index)
    sign_lord = get_sign_lord(sign_index)

    exalt_sign, exalt_degree = EXALTATION[planet]
    debil_sign, debil_degree = DEBILITATION[planet]
    mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]

    # Dignity is based on the entire exaltation/debilitation sign.
    # The exact degree is the deepest exaltation/debilitation point.
    if sign_index == exalt_sign:
        dignity = "exalted"
        score = DIGNITY_SCORES[dignity]
    elif sign_index == debil_sign:
        dignity = "debilitated"
        score = DIGNITY_SCORES[dignity]
    elif sign_index == mt_sign and mt_start <= degree_in_sign < mt_end:
        dignity = "moolatrikona"
        score = DIGNITY_SCORES[dignity]
    elif sign_index in OWN_SIGNS[planet]:
        dignity = "own_sign"
        score = DIGNITY_SCORES[dignity]
    else:
        relationship = NATURAL_RELATIONSHIPS[planet]

        if sign_lord in relationship["friends"]:
            dignity = "friendly_sign"
            score = DIGNITY_SCORES[dignity]
        elif sign_lord in relationship["enemies"]:
            dignity = "enemy_sign"
            score = DIGNITY_SCORES[dignity]
        else:
            dignity = "neutral_sign"
            score = DIGNITY_SCORES[dignity]

    return {
        "planet": planet,
        "sign": sign_name,
        "sign_index": sign_index,
        "degree_in_sign": round(degree_in_sign, 6),
        "sign_lord": sign_lord,
        "dignity": dignity,
        "dignity_score": score,
        "exaltation_sign": get_sign_name(exalt_sign),
        "exaltation_degree": exalt_degree,
        "is_deep_exaltation": abs(degree_in_sign - exalt_degree) < 0.0001,
        "debilitation_sign": get_sign_name(debil_sign),
        "debilitation_degree": debil_degree,
        "is_deep_debilitation": abs(degree_in_sign - debil_degree) < 0.0001,
    }


def angular_distance(longitude1: float, longitude2: float) -> float:
    """Return the smallest angular distance between two longitudes."""
    difference = abs(float(longitude1) - float(longitude2)) % 360.0
    return min(difference, 360.0 - difference)


def calculate_combustion(
    planet: str,
    planet_data: Dict[str, Any],
    sun_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate basic combustion from angular distance to the Sun."""
    if planet == "Sun":
        return {
            "combust": False,
            "distance_from_sun": 0.0,
            "combustion_limit": None,
            "status": "not_applicable",
        }

    limit = COMBUSTION_LIMITS.get(planet)

    if limit is None:
        return {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": None,
            "status": "not_applicable",
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
        planet_data["longitude"],
        sun_data["longitude"],
    )

    return {
        "combust": distance <= limit,
        "distance_from_sun": round(distance, 6),
        "combustion_limit": limit,
        "status": "calculated",
    }


def calculate_planetary_strength(
    planet: str,
    planet_data: Dict[str, Any],
    sun_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Calculate dignity and basic strength information for one planet."""
    sign_index = get_sign_index(planet_data)
    degree_in_sign = get_degree_in_sign(planet_data)

    dignity = calculate_dignity(
        planet=planet,
        sign_index=sign_index,
        degree_in_sign=degree_in_sign,
    )

    result = {
        **dignity,
        "retrograde": bool(planet_data.get("retrograde", False)),
        "combustion": {
            "combust": False,
            "distance_from_sun": None,
            "combustion_limit": None,
            "status": "not_calculated",
        },
    }

    if sun_data is not None:
        result["combustion"] = calculate_combustion(
            planet=planet,
            planet_data=planet_data,
            sun_data=sun_data,
        )

    return result


def calculate_planetary_strengths(
    planets_data: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Calculate planetary dignity/strength for all supported planets."""
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


def calculate_strength(
    planets_data: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Public integration alias for later use by main.py."""
    return calculate_planetary_strengths(planets_data)
