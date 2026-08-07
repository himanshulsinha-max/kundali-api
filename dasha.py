DASHA_ORDER = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17)
]


def get_mahadasha(moon_nakshatra):

    lord = moon_nakshatra["lord"]

    for planet, years in DASHA_ORDER:
        if planet == lord:
            return {
                "current_mahadasha": planet,
                "duration_years": years
            }

    return None
