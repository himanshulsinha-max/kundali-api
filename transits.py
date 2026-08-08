"""
Transit Engine
--------------

Calculates current/historical/future sidereal planetary positions
using Swiss Ephemeris and Lahiri Ayanamsha.

This module is intentionally limited to astronomical transit data.

It does NOT:
- interpret transits
- calculate Sade Sati
- calculate Saturn return
- calculate Jupiter effects
- make predictions

Those belong to the later rule/AI layer.
"""

import swisseph as swe


# ---------------------------------------------------------
# Zodiac signs
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Planets
#
# Same planetary set as planets.py
# ---------------------------------------------------------

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}


# ---------------------------------------------------------
# Lahiri
# ---------------------------------------------------------

swe.set_sid_mode(swe.SIDM_LAHIRI)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_longitude(longitude):
    """
    Keep longitude between 0 and 360 degrees.
    """
    return longitude % 360.0


def get_sign_index(longitude):
    """
    Return zodiac sign index from sidereal longitude.
    """
    longitude = normalize_longitude(longitude)
    return int(longitude // 30)


def get_sign_name(longitude):
    """
    Return zodiac sign name.
    """
    return SIGNS[get_sign_index(longitude)]


def get_sign_degree(longitude):
    """
    Return degree within current zodiac sign.
    """
    longitude = normalize_longitude(longitude)
    return longitude % 30.0


def decimal_to_dms(decimal_degree):
    """
    Convert decimal degree to DMS.
    """

    decimal_degree = abs(float(decimal_degree))

    degrees = int(decimal_degree)

    minutes_float = (
        decimal_degree - degrees
    ) * 60.0

    minutes = int(minutes_float)

    seconds = round(
        (minutes_float - minutes) * 60.0,
        2
    )

    if seconds >= 60:
        seconds = 0
        minutes += 1

    if minutes >= 60:
        minutes = 0
        degrees += 1

    return {
        "degrees": degrees,
        "minutes": minutes,
        "seconds": seconds,
    }


# ---------------------------------------------------------
# Single planetary calculation
# ---------------------------------------------------------

def calculate_transit_planet(
    julian_day,
    planet
):
    """
    Calculate one sidereal transit planet.
    """

    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
        | swe.FLG_SPEED
    )

    values, ret_flags = swe.calc_ut(
        julian_day,
        planet,
        flags
    )

    longitude = normalize_longitude(values[0])

    latitude = values[1]

    distance = values[2]

    speed = values[3]

    sign_index = get_sign_index(longitude)

    sign_name = SIGNS[sign_index]

    degree_in_sign = get_sign_degree(longitude)

    return {
        "longitude": round(longitude, 8),

        "latitude": round(latitude, 8),

        "distance": round(distance, 8),

        "sign": sign_name,

        "sign_index": sign_index,

        "degree_in_sign": round(
            degree_in_sign,
            8
        ),

        "degree_dms": decimal_to_dms(
            degree_in_sign
        ),

        "speed": round(speed, 8),

        "retrograde": speed < 0,

        "ephemeris_flags": ret_flags,
    }


# ---------------------------------------------------------
# Complete transit calculation
# ---------------------------------------------------------

def calculate_transits(julian_day):
    """
    Calculate all transit planets for a given Julian Day.

    Input:
        Julian Day in UT

    Output:
        Structured sidereal transit positions.
    """

    result = {}

    for name, planet in PLANETS.items():

        result[name] = calculate_transit_planet(
            julian_day,
            planet
        )

    # -----------------------------------------------------
    # Ketu
    #
    # Ketu is exactly 180 degrees from Rahu,
    # matching the existing planets.py architecture.
    # -----------------------------------------------------

    rahu_longitude = result["Rahu"]["longitude"]

    ketu_longitude = normalize_longitude(
        rahu_longitude + 180.0
    )

    ketu_sign_index = get_sign_index(
        ketu_longitude
    )

    ketu_degree = get_sign_degree(
        ketu_longitude
    )

    result["Ketu"] = {
        "longitude": round(
            ketu_longitude,
            8
        ),

        "latitude": round(
            -result["Rahu"]["latitude"],
            8
        ),

        "distance": result["Rahu"]["distance"],

        "sign": SIGNS[ketu_sign_index],

        "sign_index": ketu_sign_index,

        "degree_in_sign": round(
            ketu_degree,
            8
        ),

        "degree_dms": decimal_to_dms(
            ketu_degree
        ),

        "speed": round(
            -result["Rahu"]["speed"],
            8
        ),

        "retrograde": result["Rahu"]["speed"] < 0,

        "ephemeris_flags": (
            result["Rahu"]["ephemeris_flags"]
        ),
    }

    return result


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------

def get_transits(julian_day):
    """
    Public API for the transit engine.
    """
    return calculate_transits(julian_day)
