from aspects import build_aspects
from planet_strength import build_planet_dignities
from functional_nature import build_functional_profiles

def build_d1_whole_sign(ascendant_sign, planets):
    planet_dignities = build_planet_dignities(
    planets
)
    functional_profiles = build_functional_profiles(
    ascendant_sign
)
    "functional_profiles": functional_profiles,

    ascendant_sign = normalize_sign(
        ascendant_sign
    )

    houses = build_houses(
        ascendant_sign
    )

    planet_house_mapping = map_planets_to_houses(
        ascendant_sign,
        planets
    )

    for planet, house_number in planet_house_mapping.items():

        houses[house_number]["planets"].append(
            planet
        )

    house_lords = build_house_lords(
        ascendant_sign
    )

    aspects = build_aspects(
        planet_house_mapping
    )

    return {
        "chart": "D1",
        "house_system": "whole_sign",

        "ascendant": {
            "sign": ascendant_sign
        },

        "houses": houses,

        "house_lords": house_lords,
        "planet_dignities": planet_dignities,

        "planet_house_mapping":
            planet_house_mapping,

        "aspects": aspects,
    }
