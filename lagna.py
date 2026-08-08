import swisseph as swe


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
    "Pisces"
]


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


def get_degree_in_sign(longitude):
    """
    Return degree within the zodiac sign.
    """
    longitude = normalize_longitude(longitude)

    return longitude % 30.0


def calculate_lagna(julian_day, latitude, longitude):

    # We only need the Ascendant.
    # D1 houses will be calculated separately
    # using Whole-Sign methodology.

    houses, ascmc = swe.houses_ex(
        julian_day,
        latitude,
        longitude,
        b'P',
        swe.FLG_SIDEREAL
    )

    asc = normalize_longitude(ascmc[0])

    return {
        "longitude": round(asc, 8),
        "sign": get_sign_name(asc),
        "sign_index": get_sign_index(asc),
        "degree_in_sign": round(get_degree_in_sign(asc), 8)
    }
