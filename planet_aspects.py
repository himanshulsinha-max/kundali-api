"""
Planetary Drishti (Aspect) Engine
---------------------------------

This module calculates Parashari-style planetary aspects as specified by
the project Masterfile.

It does NOT decide whether a Yoga or Dosha exists.

Masterfile rules:
- All planets: 7th aspect.
- Mars: 4th, 7th, 8th.
- Jupiter: 5th, 7th, 9th.
- Saturn: 3rd, 7th, 10th.
- Rahu/Ketu: 5th, 7th, 9th.

The Masterfile also specifies that the aspect peaks at the exact degree
occupied by the aspecting planet. Therefore this module keeps:
- target house
- target sign
- exact target longitude
- degree difference from the target planet

No arbitrary orb or percentage-strength formula is introduced here.
"""

from typing import Any, Dict, List, Optional, Tuple


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

# 1-based aspect house numbers from the aspecting planet.
ASPECT_HOUSES = {
    "Sun": (7,),
    "Moon": (7,),
    "Mars": (4, 7, 8),
    "Mercury": (7,),
    "Jupiter": (5, 7, 9),
    "Venus": (7,),
    "Saturn": (3, 7, 10),
    "Rahu": (5, 7, 9),
    "Ketu": (5, 7, 9),
}

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


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into [0, 360)."""
    value = float(longitude) % 360.0
    return round(value, 10)


def angular_separation(longitude_a: float, longitude_b: float) -> float:
    """
    Minimum angular separation between two longitudes, 0..180 degrees.
    """
    difference = abs(
        normalize_longitude(longitude_a)
        - normalize_longitude(longitude_b)
    )

    if difference > 180.0:
        difference = 360.0 - difference

    return round(difference, 6)


def signed_angular_difference(
    target_longitude: float,
    exact_longitude: float,
) -> float:
    """
    Signed shortest difference target - exact in [-180, 180].
    """
    difference = (
        normalize_longitude(target_longitude)
        - normalize_longitude(exact_longitude)
    )

    if difference > 180.0:
        difference -= 360.0
    elif difference < -180.0:
        difference += 360.0

    return round(difference, 6)


def get_aspect_houses(planet_name: str) -> Tuple[int, ...]:
    """
    Return the house numbers aspected by a planet.
    """
    return ASPECT_HOUSES.get(planet_name, ())


def aspect_type(planet_name: str, aspect_house: int) -> str:
    """
    Label the aspect as primary or special.
    """
    if aspect_house == 7:
        return "primary_7th"

    return "special"


def target_sign_from_source(
    source_sign_index: int,
    aspect_house: int,
) -> int:
    """
    Calculate the target sign index for a Whole-Sign aspect.

    Example:
        source sign = Aries (0)
        7th aspect   = Libra (6)
    """
    if not 0 <= int(source_sign_index) <= 11:
        raise ValueError("source_sign_index must be between 0 and 11")

    # House 1 is the source sign itself.
    offset = int(aspect_house) - 1
    return (int(source_sign_index) + offset) % 12


def exact_aspect_longitude(
    source_longitude: float,
    aspect_house: int,
) -> float:
    """
    Calculate the exact degree where the aspect peaks.

    The Masterfile states that an aspect lands at the same degree in
    the target house/sign as the aspecting planet.
    """
    offset = (int(aspect_house) - 1) * 30.0
    return normalize_longitude(float(source_longitude) + offset)


def extract_house(
    planet_data: Dict[str, Any],
) -> Optional[int]:
    """
    Read a house value from common supported structures.
    """
    for key in ("house", "house_number"):
        value = planet_data.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass

    return None


def build_planet_aspect(
    source_name: str,
    source_data: Dict[str, Any],
    aspect_house: int,
) -> Optional[Dict[str, Any]]:
    """
    Build one directional planet -> house aspect record.
    """
    source_sign_index = source_data.get("sign_index")
    source_longitude = source_data.get("longitude")
    source_degree = source_data.get("degree_in_sign")

    if source_sign_index is None or source_longitude is None:
        return None

    target_sign_index = target_sign_from_source(
        int(source_sign_index),
        aspect_house,
    )

    exact_longitude = exact_aspect_longitude(
        float(source_longitude),
        aspect_house,
    )

    target_sign = SIGNS[target_sign_index]

    return {
        "source_planet": source_name,
        "source_house": extract_house(source_data),
        "source_sign": source_data.get("sign")
        or SIGNS[int(source_sign_index)],
        "source_sign_index": int(source_sign_index),
        "source_longitude": round(float(source_longitude), 6),
        "source_degree_in_sign": (
            round(float(source_degree), 6)
            if source_degree is not None
            else None
        ),
        "target_house_from_source": int(aspect_house),
        "target_sign": target_sign,
        "target_sign_index": target_sign_index,
        "exact_target_longitude": exact_longitude,
        "aspect_type": aspect_type(source_name, aspect_house),
        "is_special_aspect": aspect_house != 7,
    }


def build_all_planet_aspects(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build every planetary aspect to its target house/sign.

    Each directional aspect appears once.
    """
    results: List[Dict[str, Any]] = []

    for planet_name in PLANETS:
        if planet_name not in planets:
            continue

        source_data = planets[planet_name]

        for house_number in get_aspect_houses(planet_name):
            record = build_planet_aspect(
                planet_name,
                source_data,
                house_number,
            )

            if record is not None:
                results.append(record)

    return results


def planet_aspects_planet(
    source_name: str,
    source_data: Dict[str, Any],
    target_name: str,
    target_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Determine whether source planet aspects target planet.

    The target planet is considered aspected when its Whole-Sign house
    from the source planet matches one of the source planet's aspect
    houses.

    If target longitude is available, exact-degree metadata is also
    returned.
    """
    source_sign_index = source_data.get("sign_index")
    target_sign_index = target_data.get("sign_index")

    if source_sign_index is None or target_sign_index is None:
        return []

    results: List[Dict[str, Any]] = []

    source_sign_index = int(source_sign_index)
    target_sign_index = int(target_sign_index)

    for aspect_house in get_aspect_houses(source_name):
        expected_target_sign = target_sign_from_source(
            source_sign_index,
            aspect_house,
        )

        if expected_target_sign != target_sign_index:
            continue

        exact_longitude = None
        degree_difference = None
        signed_difference = None

        if source_data.get("longitude") is not None:
            exact_longitude = exact_aspect_longitude(
                float(source_data["longitude"]),
                aspect_house,
            )

            if target_data.get("longitude") is not None:
                degree_difference = angular_separation(
                    float(target_data["longitude"]),
                    exact_longitude,
                )
                signed_difference = signed_angular_difference(
                    float(target_data["longitude"]),
                    exact_longitude,
                )

        results.append({
            "source_planet": source_name,
            "target_planet": target_name,
            "aspect_house": int(aspect_house),
            "aspect_type": aspect_type(
                source_name,
                aspect_house,
            ),
            "is_special_aspect": aspect_house != 7,
            "source_sign": (
                source_data.get("sign")
                or SIGNS[source_sign_index]
            ),
            "target_sign": (
                target_data.get("sign")
                or SIGNS[target_sign_index]
            ),
            "source_sign_index": source_sign_index,
            "target_sign_index": target_sign_index,
            "exact_target_longitude": exact_longitude,
            "target_longitude": (
                round(float(target_data["longitude"]), 6)
                if target_data.get("longitude") is not None
                else None
            ),
            "degree_difference_from_exact_aspect": degree_difference,
            "signed_degree_difference": signed_difference,
        })

    return results


def build_planet_to_planet_aspects(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build all directional planet -> planet aspects.

    Unlike conjunction pairs, aspects are directional:
        Jupiter -> Mars
    is different from:
        Mars -> Jupiter
    """
    results: List[Dict[str, Any]] = []

    available = [
        planet
        for planet in PLANETS
        if planet in planets
    ]

    for source_name in available:
        for target_name in available:
            if source_name == target_name:
                continue

            results.extend(
                planet_aspects_planet(
                    source_name,
                    planets[source_name],
                    target_name,
                    planets[target_name],
                )
            )

    return results


def build_mutual_aspects(
    planet_to_planet_aspects: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Identify pairs where both planets aspect one another.
    """
    indexed = {
        (
            item["source_planet"],
            item["target_planet"],
        ): item
        for item in planet_to_planet_aspects
    }

    results: List[Dict[str, Any]] = []
    seen = set()

    for key, forward in indexed.items():
        source, target = key
        reverse_key = (target, source)

        if reverse_key not in indexed:
            continue

        pair = tuple(sorted((source, target)))

        if pair in seen:
            continue

        seen.add(pair)

        reverse = indexed[reverse_key]

        results.append({
            "planet_a": source,
            "planet_b": target,
            "mutual_aspect": True,
            "a_to_b": forward,
            "b_to_a": reverse,
        })

    return results


def get_planets_aspected_by(
    source_planet: str,
    planet_to_planet_aspects: List[Dict[str, Any]],
) -> List[str]:
    """Return planets receiving aspects from source_planet."""
    return [
        item["target_planet"]
        for item in planet_to_planet_aspects
        if item["source_planet"] == source_planet
    ]


def get_planets_aspecting(
    target_planet: str,
    planet_to_planet_aspects: List[Dict[str, Any]],
) -> List[str]:
    """Return planets that aspect target_planet."""
    return [
        item["source_planet"]
        for item in planet_to_planet_aspects
        if item["target_planet"] == target_planet
    ]


def get_aspects_to_house(
    source_planet: str,
    aspects: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Return all house aspects cast by source_planet.
    """
    return [
        item
        for item in aspects
        if item["source_planet"] == source_planet
    ]


def build_aspect_engine(
    planets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Master aspect calculation function.

    Returns:
        planet_to_house
        planet_to_planet
        mutual_aspects
    """
    planet_to_house = build_all_planet_aspects(planets)
    planet_to_planet = build_planet_to_planet_aspects(planets)
    mutual_aspects = build_mutual_aspects(planet_to_planet)

    return {
        "planet_to_house": planet_to_house,
        "planet_to_planet": planet_to_planet,
        "mutual_aspects": mutual_aspects,
    }


# ---------------------------------------------------------------------
# Compatibility aliases
# ---------------------------------------------------------------------

def build_planet_aspects(
    planets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Alias for build_aspect_engine()."""
    return build_aspect_engine(planets)
