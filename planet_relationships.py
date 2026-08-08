"""
Planet Relationship Engine
--------------------------

Builds the relationship data layer required by later Yoga detection.

This module does NOT decide whether a Yoga exists.

It calculates:
- Planet-to-planet conjunction/association
- Planet-to-sign-lord relationships
- Planet-to-house-lord relationships
- Natural planetary relationships
- Functional planetary relationships
- House-based relationships

Designed to work with:
    planets.py
    lagna.py
    d1_whole_sign.py
"""

from typing import Dict, Any, List, Optional


# ---------------------------------------------------------------------
# PLANETS
# ---------------------------------------------------------------------

PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]


# ---------------------------------------------------------------------
# NATURAL PLANETARY RELATIONSHIPS
# ---------------------------------------------------------------------
#
# Classical Parashari-style natural relationships.
#
# Each planet has:
#   friends
#   enemies
#   neutrals
#
# Rahu/Ketu are kept separately as their natural relationship treatment
# varies across classical traditions. We therefore do not force them into
# the same deterministic friendship table.
# ---------------------------------------------------------------------

NATURAL_RELATIONSHIPS = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "enemies": ["Venus", "Saturn"],
        "neutrals": ["Mercury"],
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "enemies": [],
        "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "enemies": ["Mercury"],
        "neutrals": ["Venus", "Saturn"],
    },
    "Mercury": {
        "friends": ["Sun", "Venus"],
        "enemies": ["Moon"],
        "neutrals": ["Mars", "Jupiter", "Saturn"],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "enemies": ["Mercury", "Venus"],
        "neutrals": ["Saturn"],
    },
    "Venus": {
        "friends": ["Mercury", "Saturn"],
        "enemies": ["Sun", "Moon"],
        "neutrals": ["Mars", "Jupiter"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutrals": ["Jupiter"],
    },
    "Rahu": {
        "friends": [],
        "enemies": [],
        "neutrals": [],
    },
    "Ketu": {
        "friends": [],
        "enemies": [],
        "neutrals": [],
    },
}


# ---------------------------------------------------------------------
# SIGN LORDS
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# SIGN INDEX LORDS
# ---------------------------------------------------------------------

SIGN_LORDS_BY_INDEX = {
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


# ---------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------

def get_sign_lord(sign: str) -> Optional[str]:
    """
    Return lord of a zodiac sign.
    """
    if sign is None:
        return None

    return SIGN_LORDS.get(sign)


def get_sign_lord_by_index(sign_index: int) -> Optional[str]:
    """
    Return sign lord using 0-11 sign index.
    """
    return SIGN_LORDS_BY_INDEX.get(sign_index)


def natural_relationship(
    planet_a: str,
    planet_b: str,
) -> str:
    """
    Return the natural relationship of planet_a toward planet_b.

    Possible values:
        friend
        enemy
        neutral
        unknown
        same_planet
    """

    if planet_a == planet_b:
        return "same_planet"

    data = NATURAL_RELATIONSHIPS.get(planet_a)

    if not data:
        return "unknown"

    if planet_b in data["friends"]:
        return "friend"

    if planet_b in data["enemies"]:
        return "enemy"

    if planet_b in data["neutrals"]:
        return "neutral"

    return "unknown"


# ---------------------------------------------------------------------
# CONJUNCTION
# ---------------------------------------------------------------------

def planets_conjunct(
    planet_a: Dict[str, Any],
    planet_b: Dict[str, Any],
) -> bool:
    """
    Determine whole-sign conjunction.

    In the D1 whole-sign framework, two planets are conjunct when they
    occupy the same sign.

    Exact degree-based conjunction is intentionally NOT used here.
    """

    return (
        planet_a.get("sign_index") is not None
        and planet_a.get("sign_index") == planet_b.get("sign_index")
    )


# ---------------------------------------------------------------------
# DEGREE SEPARATION
# ---------------------------------------------------------------------

def degree_separation(
    planet_a: Dict[str, Any],
    planet_b: Dict[str, Any],
) -> Optional[float]:
    """
    Calculate absolute longitudinal separation.

    This is useful later for more precise association/aspect logic.
    """

    longitude_a = planet_a.get("longitude")
    longitude_b = planet_b.get("longitude")

    if longitude_a is None or longitude_b is None:
        return None

    difference = abs(longitude_a - longitude_b)

    if difference > 180:
        difference = 360 - difference

    return round(difference, 6)


# ---------------------------------------------------------------------
# PLANET-TO-PLANET RELATIONSHIP
# ---------------------------------------------------------------------

def build_planet_relationship(
    planet_a_name: str,
    planet_a: Dict[str, Any],
    planet_b_name: str,
    planet_b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a normalized relationship record between two planets.
    """

    separation = degree_separation(
        planet_a,
        planet_b,
    )

    conjunct = planets_conjunct(
        planet_a,
        planet_b,
    )

    return {
        "planet_a": planet_a_name,
        "planet_b": planet_b_name,

        "same_sign": conjunct,

        "degree_separation": separation,

        "natural_relationship": natural_relationship(
            planet_a_name,
            planet_b_name,
        ),

        "reverse_natural_relationship": natural_relationship(
            planet_b_name,
            planet_a_name,
        ),
    }


# ---------------------------------------------------------------------
# ALL PLANET-TO-PLANET RELATIONSHIPS
# ---------------------------------------------------------------------

def build_planet_to_planet_relationships(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build unique pairwise relationships.

    Example:

        Sun-Mars
        Sun-Jupiter
        Moon-Mars
        ...

    Each pair appears only once.
    """

    available_planets = [
        planet
        for planet in PLANETS
        if planet in planets
    ]

    relationships = []

    for i, planet_a_name in enumerate(available_planets):

        for planet_b_name in available_planets[i + 1:]:

            relationship = build_planet_relationship(
                planet_a_name,
                planets[planet_a_name],
                planet_b_name,
                planets[planet_b_name],
            )

            relationships.append(relationship)

    return relationships


# ---------------------------------------------------------------------
# PLANET -> SIGN LORD
# ---------------------------------------------------------------------

def build_planet_sign_lord_relationship(
    planet_name: str,
    planet_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine the relationship between a planet and the lord of the sign
    it occupies.
    """

    sign = planet_data.get("sign")

    sign_index = planet_data.get("sign_index")

    if sign:
        lord = get_sign_lord(sign)
    elif sign_index is not None:
        lord = get_sign_lord_by_index(sign_index)
    else:
        lord = None

    if lord is None:
        return {
            "planet": planet_name,
            "sign": sign,
            "sign_lord": None,
            "natural_relationship": "unknown",
        }

    return {
        "planet": planet_name,
        "sign": sign,
        "sign_lord": lord,
        "natural_relationship": natural_relationship(
            planet_name,
            lord,
        ),
    }


def build_all_sign_lord_relationships(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build sign-lord relationships for all planets.
    """

    relationships = []

    for planet_name in PLANETS:

        if planet_name not in planets:
            continue

        relationships.append(
            build_planet_sign_lord_relationship(
                planet_name,
                planets[planet_name],
            )
        )

    return relationships


# ---------------------------------------------------------------------
# HOUSE LORD RELATIONSHIP
# ---------------------------------------------------------------------

def build_house_lord_relationships(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
) -> List[Dict[str, Any]]:
    """
    Determine relationships between planets and house lords.

    This is critical for future Yoga detection.

    Example:

        Mars is 1st lord
        Jupiter is 5th lord
        Mars conjunct Jupiter

    The Yoga engine can later consume this relationship data.
    """

    relationships = []

    for house_number, lord in house_lords.items():

        for planet_name in PLANETS:

            if planet_name not in planets:
                continue

            relationship = natural_relationship(
                planet_name,
                lord,
            )

            relationships.append({
                "house": house_number,
                "house_lord": lord,
                "planet": planet_name,
                "natural_relationship": relationship,
                "same_planet": planet_name == lord,
            })

    return relationships


# ---------------------------------------------------------------------
# PLANET -> HOUSE OCCUPANCY RELATIONSHIP
# ---------------------------------------------------------------------

def build_planet_house_relationships(
    planets: Dict[str, Dict[str, Any]],
    planet_house_mapping: Dict[str, Any],
    house_lords: Dict[int, str],
) -> List[Dict[str, Any]]:
    """
    Connect every planet with:
        - its house
        - that house's lord
        - its relationship with the house lord

    This becomes a major input to Yoga detection.
    """

    relationships = []

    for planet_name, planet_data in planets.items():

        house = planet_house_mapping.get(planet_name)

        if isinstance(house, dict):
            house_number = house.get("house")
        else:
            house_number = house

        if house_number is None:
            continue

        house_lord = house_lords.get(house_number)

        relationships.append({
            "planet": planet_name,
            "house": house_number,
            "house_lord": house_lord,
            "planet_is_house_lord": planet_name == house_lord,
            "natural_relationship": (
                natural_relationship(
                    planet_name,
                    house_lord,
                )
                if house_lord
                else "unknown"
            ),
        })

    return relationships


# ---------------------------------------------------------------------
# MASTER RELATIONSHIP ENGINE
# ---------------------------------------------------------------------

def build_planet_relationships(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Optional[Dict[int, str]] = None,
    planet_house_mapping: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Master function.

    Returns the complete relationship data layer.
    """

    result = {
        "planet_to_planet": build_planet_to_planet_relationships(
            planets
        ),

        "planet_to_sign_lord": build_all_sign_lord_relationships(
            planets
        ),

        "planet_to_house_lord": [],

        "planet_to_house": [],
    }

    if house_lords:
        result["planet_to_house_lord"] = (
            build_house_lord_relationships(
                planets,
                house_lords,
            )
        )

    if planet_house_mapping and house_lords:
        result["planet_to_house"] = (
            build_planet_house_relationships(
                planets,
                planet_house_mapping,
                house_lords,
            )
        )

    return result


# ---------------------------------------------------------------------
# SIMPLE CONVENIENCE FUNCTIONS FOR FUTURE YOGA ENGINE
# ---------------------------------------------------------------------

def get_conjunct_planets(
    planet_name: str,
    relationships: List[Dict[str, Any]],
) -> List[str]:
    """
    Return planets occupying the same sign as the requested planet.
    """

    result = []

    for relationship in relationships:

        if not relationship["same_sign"]:
            continue

        if relationship["planet_a"] == planet_name:
            result.append(relationship["planet_b"])

        elif relationship["planet_b"] == planet_name:
            result.append(relationship["planet_a"])

    return result


def get_planet_relationship(
    planet_a: str,
    planet_b: str,
    relationships: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific planet-to-planet relationship.
    """

    for relationship in relationships:

        same_direction = (
            relationship["planet_a"] == planet_a
            and relationship["planet_b"] == planet_b
        )

        reverse_direction = (
            relationship["planet_a"] == planet_b
            and relationship["planet_b"] == planet_a
        )

        if same_direction or reverse_direction:
            return relationship

    return None
