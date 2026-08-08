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
    "Pisces",
]


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


def normalize_longitude(longitude):
    """Keep longitude between 0 and 360 degrees."""
    return longitude % 360.0


def get_sign_index(longitude):
    """Return zodiac sign index from sidereal longitude."""
    longitude = normalize_longitude(longitude)
    return int(longitude // 30)


def get_sign_name(longitude):
    """Return zodiac sign name."""
    return SIGNS[get_sign_index(longitude)]


def get_sign_degree(longitude):
    """Return degree within the current zodiac sign."""
    longitude = normalize_longitude(longitude)
    return longitude % 30.0


def decimal_to_dms(decimal_degree):
    """Convert decimal degrees to degrees, minutes and seconds."""

    decimal_degree = abs(decimal_degree)

    degrees = int(decimal_degree)
    minutes_float = (decimal_degree - degrees) * 60
    minutes = int(minutes_float)
    seconds = round((minutes_float - minutes) * 60, 2)

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


def calculate_planets(julian_day):

    result = {}

    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
        | swe.FLG_SPEED
    )

    for name, planet in PLANETS.items():

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
        sign_degree = get_sign_degree(longitude)

        result[name] = {
            "longitude": round(longitude, 8),
            "latitude": round(latitude, 8),
            "distance": round(distance, 8),

            "sign": sign_name,
            "sign_index": sign_index,

            "degree_in_sign": round(sign_degree, 8),
            "degree_dms": decimal_to_dms(sign_degree),

            "speed": round(speed, 8),
            "retrograde": speed < 0,

            "ephemeris_flags": ret_flags,
        }

    # ---------------------------------
    # Ketu = exactly 180° from Rahu
    # ---------------------------------

    rahu_longitude = result["Rahu"]["longitude"]

    ketu_longitude = normalize_longitude(
        rahu_longitude + 180.0
    )

    ketu_sign_index = get_sign_index(ketu_longitude)
    ketu_sign_degree = get_sign_degree(ketu_longitude)

    result["Ketu"] = {
        "longitude": round(ketu_longitude, 8),
        "latitude": round(-result["Rahu"]["latitude"], 8),
        "distance": result["Rahu"]["distance"],

        "sign": SIGNS[ketu_sign_index],
        "sign_index": ketu_sign_index,

        "degree_in_sign": round(ketu_sign_degree, 8),
        "degree_dms": decimal_to_dms(ketu_sign_degree),

        "speed": round(-result["Rahu"]["speed"], 8),
        "retrograde": result["Rahu"]["speed"] < 0,

        "ephemeris_flags": result["Rahu"]["ephemeris_flags"],
    }

    return result
