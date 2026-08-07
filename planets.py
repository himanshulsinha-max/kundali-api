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

def get_sign_name(longitude):
    return SIGNS[int(longitude // 30)]

def calculate_planets(julian_day):

    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    result = {}

    for name, planet in planets.items():
        longitude = swe.calc_ut(
            julian_day,
            planet,
            swe.FLG_SIDEREAL
        )[0][0]

        result[name] = {
            "longitude": round(longitude, 2),
            "sign": get_sign_name(longitude)
        }

    ketu_longitude = (result["Rahu"]["longitude"] + 180) % 360

    result["Ketu"] = {
        "longitude": round(ketu_longitude, 2),
        "sign": get_sign_name(ketu_longitude)
    }

    return result
