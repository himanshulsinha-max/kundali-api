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

def calculate_lagna(julian_day, latitude, longitude):

    houses, ascmc = swe.houses_ex(
        julian_day,
        latitude,
        longitude,
        b'P',
        swe.FLG_SIDEREAL
    )

    asc = ascmc[0]

    return {
        "longitude": round(asc, 2),
        "sign": get_sign_name(asc)
    }
