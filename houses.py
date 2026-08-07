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


def calculate_houses(julian_day, lat, lon):

    houses, ascmc = swe.houses_ex(
        julian_day,
        lat,
        lon,
        b'P',
        swe.FLG_SIDEREAL
    )

    result = {}

    for i in range(12):
        longitude = houses[i]

        result[f"House_{i+1}"] = {
            "longitude": round(longitude, 2),
            "sign": get_sign_name(longitude)
        }

    return result
