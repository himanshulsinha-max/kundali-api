"""
Transit Facts Engine
--------------------

Builds structured, interpretation-neutral Vedic transit facts
from:

1. Existing natal chart data
2. Existing Swiss Ephemeris transit data from transits.py

Design principles:
- Swiss Ephemeris remains the astronomical source.
- Lahiri sidereal positions are assumed.
- D1 uses Whole-Sign houses.
- This module generates FACTS, not predictions.
- No web data is used.
- No AI interpretation is performed here.

The interpretation/AI layer can consume the returned facts later.
"""

from typing import Any, Dict, Optional


# -------------------------------------------------------------------
# Zodiac
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
# Classical Vedic graha drishti
#
# All planets: 7th aspect
# Mars: 4th and 8th
# Jupiter: 5th and 9th
# Saturn: 3rd and 10th
#
# Rahu/Ketu are intentionally excluded from special graha drishti
# here. Their treatment can be added later as a separate rule layer.
# -------------------------------------------------------------------

SPECIAL_ASPECTS = {
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
}

DEFAULT_ASPECTS = [7]


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def normalize_sign_index(sign_index: int) -> int:
    """Normalize a zodiac sign index to 0-11."""
    return int(sign_index) % 12


def sign_index_from_name(sign_name: str) -> int:
    """Return zodiac index for a sign name."""
    if sign_name not in SIGNS:
        raise ValueError(f"Unknown zodiac sign: {sign_name}")
    return SIGNS.index(sign_name)


def sign_name_from_index(sign_index: int) -> str:
    """Return zodiac sign name from index."""
    return SIGNS[normalize_sign_index(sign_index)]


def get_sign_index_from_planet(planet_data: Dict[str, Any]) -> Optional[int]:
    """
    Extract sign index from an existing planetary record.

    Existing project modules normally expose sign_index.
    Falls back to sign name when necessary.
    """
    if not isinstance(planet_data, dict):
        return None

    if "sign_index" in planet_data:
        return normalize_sign_index(
            int(planet_data["sign_index"])
        )

    if "sign" in planet_data:
        return sign_index_from_name(
            planet_data["sign"]
        )

    return None


def get_longitude(planet_data: Dict[str, Any]) -> Optional[float]:
    """Extract longitude when available."""
    if not isinstance(planet_data, dict):
        return None

    longitude = planet_data.get("longitude")

    if longitude is None:
        return None

    return float(longitude) % 360.0


def whole_sign_house(
    planet_sign_index: int,
    lagna_sign_index: int,
) -> int:
    """
    Calculate Whole-Sign house number.

    Lagna sign = 1st house.
    Next sign = 2nd house, etc.
    """
    return (
        (planet_sign_index - lagna_sign_index) % 12
    ) + 1


def circular_sign_distance(
    from_sign: int,
    to_sign: int,
) -> int:
    """
    Count zodiac signs from from_sign to to_sign.

    Same sign = 1
    Next sign = 2
    ...
    """
    return (
        (to_sign - from_sign) % 12
    ) + 1


def get_aspect_numbers(planet_name: str):
    """
    Return classical Vedic graha-drishti aspect numbers.
    """
    return SPECIAL_ASPECTS.get(
        planet_name,
        DEFAULT_ASPECTS,
    )


def planet_aspects_sign(
    planet_name: str,
    planet_sign_index: int,
    target_sign_index: int,
) -> bool:
    """
    Determine whether a planet gives classical Vedic graha drishti
    to the target sign.
    """
    distance = circular_sign_distance(
        planet_sign_index,
        target_sign_index,
    )

    return distance in get_aspect_numbers(planet_name)


# -------------------------------------------------------------------
# Transit -> natal planet facts
# -------------------------------------------------------------------

def build_transit_natal_contacts(
    transit_planets: Dict[str, Any],
    natal_planets: Dict[str, Any],
) -> list:
    """
    Identify sign-level transit/natal contacts and classical
    Vedic graha-drishti contacts.

    This function reports facts only.

    It does NOT assign:
    - good/bad
    - benefic/malefic result
    - prediction
    - event
    - severity
    """

    contacts = []

    for transit_name, transit_data in transit_planets.items():

        transit_sign = get_sign_index_from_planet(
            transit_data
        )

        if transit_sign is None:
            continue

        transit_longitude = get_longitude(
            transit_data
        )

        for natal_name, natal_data in natal_planets.items():

            natal_sign = get_sign_index_from_planet(
                natal_data
            )

            if natal_sign is None:
                continue

            natal_longitude = get_longitude(
                natal_data
            )

            # -------------------------------------------------------
            # Same-sign contact
            # -------------------------------------------------------

            same_sign = (
                transit_sign == natal_sign
            )

            # -------------------------------------------------------
            # Exact longitude difference
            # -------------------------------------------------------

            longitude_difference = None

            if (
                transit_longitude is not None
                and natal_longitude is not None
            ):
                difference = abs(
                    transit_longitude
                    - natal_longitude
                )

                longitude_difference = min(
                    difference,
                    360.0 - difference,
                )

            # -------------------------------------------------------
            # Vedic graha drishti
            # -------------------------------------------------------

            graha_drishti = planet_aspects_sign(
                transit_name,
                transit_sign,
                natal_sign,
            )

            if same_sign or graha_drishti:

                contact_type = []

                if same_sign:
                    contact_type.append(
                        "same_sign"
                    )

                if graha_drishti:
                    contact_type.append(
                        "graha_drishti"
                    )

                contacts.append(
                    {
                        "transit_planet": transit_name,
                        "natal_planet": natal_name,
                        "transit_sign": sign_name_from_index(
                            transit_sign
                        ),
                        "natal_sign": sign_name_from_index(
                            natal_sign
                        ),
                        "contact_type": contact_type,
                        "longitude_difference": (
                            round(
                                longitude_difference,
                                4,
                            )
                            if longitude_difference
                            is not None
                            else None
                        ),
                    }
                )

    return contacts


# -------------------------------------------------------------------
# Transit -> Lagna / houses
# -------------------------------------------------------------------

def build_transit_house_facts(
    transit_planets: Dict[str, Any],
    lagna: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Map each transit planet to its Whole-Sign house from natal Lagna.
    """

    lagna_sign_index = get_sign_index_from_planet(
        lagna
    )

    if lagna_sign_index is None:

        if isinstance(lagna, dict):
            if "sign" in lagna:
                lagna_sign_index = sign_index_from_name(
                    lagna["sign"]
                )

        if lagna_sign_index is None:
            raise ValueError(
                "Lagna must contain sign_index or sign."
            )

    facts = {}

    for planet_name, planet_data in transit_planets.items():

        transit_sign_index = get_sign_index_from_planet(
            planet_data
        )

        if transit_sign_index is None:
            continue

        house_number = whole_sign_house(
            transit_sign_index,
            lagna_sign_index,
        )

        facts[planet_name] = {
            "sign": sign_name_from_index(
                transit_sign_index
            ),
            "sign_index": transit_sign_index,
            "house_from_lagna": house_number,
            "retrograde": bool(
                planet_data.get(
                    "retrograde",
                    False,
                )
            ),
            "speed": planet_data.get(
                "speed"
            ),
            "longitude": planet_data.get(
                "longitude"
            ),
            "degree_in_sign": planet_data.get(
                "degree_in_sign"
            ),
        }

    return facts


# -------------------------------------------------------------------
# Transit sign ingress facts
# -------------------------------------------------------------------

def build_transit_sign_facts(
    transit_planets: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Return normalized sign/degree facts for every transit planet.
    """

    result = {}

    for planet_name, planet_data in transit_planets.items():

        sign_index = get_sign_index_from_planet(
            planet_data
        )

        if sign_index is None:
            continue

        result[planet_name] = {
            "sign": sign_name_from_index(
                sign_index
            ),
            "sign_index": sign_index,
            "longitude": planet_data.get(
                "longitude"
            ),
            "degree_in_sign": planet_data.get(
                "degree_in_sign"
            ),
            "degree_dms": planet_data.get(
                "degree_dms"
            ),
            "retrograde": bool(
                planet_data.get(
                    "retrograde",
                    False,
                )
            ),
            "speed": planet_data.get(
                "speed"
            ),
        }

    return result


# -------------------------------------------------------------------
# Retrograde facts
# -------------------------------------------------------------------

def build_retrograde_facts(
    transit_planets: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Return explicit retrograde status for each transit planet.
    """

    return {
        planet_name: bool(
            planet_data.get(
                "retrograde",
                False,
            )
        )
        for planet_name, planet_data
        in transit_planets.items()
    }


# -------------------------------------------------------------------
# Transit aspect facts
# -------------------------------------------------------------------

def build_transit_aspect_facts(
    transit_planets: Dict[str, Any],
) -> list:
    """
    Build planet-to-sign graha-drishti facts.

    This is deliberately structural.

    Example:
        Saturn in Aries aspects:
        Gemini, Libra and Scorpio

    depending on the classical aspect positions.
    """

    aspects = []

    for planet_name, planet_data in transit_planets.items():

        sign_index = get_sign_index_from_planet(
            planet_data
        )

        if sign_index is None:
            continue

        aspect_numbers = get_aspect_numbers(
            planet_name
        )

        for aspect_number in aspect_numbers:

            target_sign_index = (
                sign_index
                + aspect_number
                - 1
            ) % 12

            aspects.append(
                {
                    "planet": planet_name,
                    "from_sign": sign_name_from_index(
                        sign_index
                    ),
                    "aspect_number": aspect_number,
                    "target_sign": sign_name_from_index(
                        target_sign_index
                    ),
                    "target_sign_index": (
                        target_sign_index
                    ),
                }
            )

    return aspects


# -------------------------------------------------------------------
# Main facts builder
# -------------------------------------------------------------------

def build_transit_facts(
    transit_planets: Dict[str, Any],
    natal_planets: Optional[
        Dict[str, Any]
    ] = None,
    lagna: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Build complete interpretation-neutral transit facts.

    Parameters
    ----------
    transit_planets:
        Output from transits.get_transits().

    natal_planets:
        Existing natal planetary data from planets.py.

    lagna:
        Existing natal Lagna data from lagna.py.

    Returns
    -------
    dict
        Structured facts for the later AI/rule interpretation layer.
    """

    if not isinstance(
        transit_planets,
        dict,
    ):
        raise TypeError(
            "transit_planets must be a dictionary."
        )

    result = {
        "engine": "transit_facts",
        "version": "1.0",
        "zodiac": "sidereal",
        "ayanamsha": "Lahiri",
        "house_system": "whole_sign",
        "interpretation": False,

        "transits": build_transit_sign_facts(
            transit_planets
        ),

        "retrograde": build_retrograde_facts(
            transit_planets
        ),

        "graha_drishti": build_transit_aspect_facts(
            transit_planets
        ),
    }

    # ---------------------------------------------------------------
    # Natal-dependent facts
    # ---------------------------------------------------------------

    if lagna is not None:

        result["houses_from_lagna"] = (
            build_transit_house_facts(
                transit_planets,
                lagna,
            )
        )

    else:

        result["houses_from_lagna"] = {}

    # ---------------------------------------------------------------
    # Transit-to-natal contacts
    # ---------------------------------------------------------------

    if natal_planets is not None:

        result["natal_contacts"] = (
            build_transit_natal_contacts(
                transit_planets,
                natal_planets,
            )
        )

    else:

        result["natal_contacts"] = []

    return result


# -------------------------------------------------------------------
# Simple public API
# -------------------------------------------------------------------

def get_transit_facts(
    transit_planets: Dict[str, Any],
    natal_planets: Optional[
        Dict[str, Any]
    ] = None,
    lagna: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Public API for the Transit Facts Engine.
    """

    return build_transit_facts(
        transit_planets=transit_planets,
        natal_planets=natal_planets,
        lagna=lagna,
    )
