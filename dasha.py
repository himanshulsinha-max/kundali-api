from datetime import datetime, timedelta

DASHA_ORDER = [
    ("Ketu",7),
    ("Venus",20),
    ("Sun",6),
    ("Moon",10),
    ("Mars",7),
    ("Rahu",18),
    ("Jupiter",16),
    ("Saturn",19),
    ("Mercury",17)
]


def get_mahadasha(moon_info, balance):

    lord = moon_info["lord"]

    years = 0

    for planet, duration in DASHA_ORDER:

        if planet == lord:
            years = duration
            break

    remaining_years = years * balance

    return {
        "lord": lord,
        "total_years": years,
        "remaining_years": round(remaining_years,2)
    }
