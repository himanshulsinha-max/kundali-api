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


PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}


def get_sign_name(longitude):
    return SIGNS[int(longitude // 30)]


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

        longitude = values[0]
        speed = values[3]

        result[name] = {
            "longitude": longitude,
            "sign": get_sign_name(longitude),
            "speed": speed,
            "retrograde": speed < 0
        }

    rahu_longitude = result["Rahu"]["longitude"]

    ketu_longitude = (rahu_longitude + 180.0) % 360.0

    result["Ketu"] = {
        "longitude": ketu_longitude,
        "sign": get_sign_name(ketu_longitude),
        "speed": -result["Rahu"]["speed"],
        "retrograde": result["Rahu"]["speed"] < 0
    }

    return result
