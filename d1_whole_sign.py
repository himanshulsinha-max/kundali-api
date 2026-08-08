def build_d1_whole_sign(ascendant_sign, planets):

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

    return {
        "chart": "D1",
        "house_system": "whole_sign",

        "ascendant": {
            "sign": ascendant_sign
        },

        "houses": houses,

        "house_lords": house_lords,

        "planet_house_mapping":
            planet_house_mapping,
    }
