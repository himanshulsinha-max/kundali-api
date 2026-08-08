# functional_nature.py

from house_lords import SIGN_LORDS


PLANETS = {
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
}


KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
TRISHADAYAS = {3, 6, 11}
MARAKA_HOUSES = {2, 7}


NATURAL_BENEFICS = {
    "Jupiter",
    "Venus",
    "Mercury",
    "Moon",
}


NATURAL_MALEFICS = {
    "Sun",
    "Mars",
    "Saturn",
}


def normalize_planet(planet):
    if not isinstance(planet, str):
        raise TypeError("Planet must be a string.")

    planet = planet.strip().title()

    if planet not in PLANETS:
        raise ValueError(
            f"Unsupported planet: {planet}"
        )

    return planet


def normalize_sign(sign):
    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGN_LORDS:
        raise ValueError(
            f"Invalid zodiac sign: {sign}"
        )

    return sign


def get_house_signs(ascendant_sign):
    """
    Return the sign occupying each Whole-Sign house.
    """

    ascendant_sign = normalize_sign(
        ascendant_sign
    )

    signs = list(SIGN_LORDS.keys())
    asc_index = signs.index(ascendant_sign)

    return {
        house: signs[
            (asc_index + house - 1) % 12
        ]
        for house in range(1, 13)
    }


def get_house_lordships(ascendant_sign):
    """
    Return all houses owned by each planet.
    """

    house_signs = get_house_signs(
        ascendant_sign
    )

    result = {
        planet: []
        for planet in PLANETS
    }

    for house, sign in house_signs.items():

        lord = SIGN_LORDS[sign]

        if lord in result:
            result[lord].append(house)

    return result


def classify_house_roles(houses):
    """
    Convert house ownership into structural roles.
    """

    return {
        "kendra": sorted(
            set(houses) & KENDRAS
        ),
        "trikona": sorted(
            set(houses) & TRIKONAS
        ),
        "dusthana": sorted(
            set(houses) & DUSTHANAS
        ),
        "trishadaya": sorted(
            set(houses) & TRISHADAYAS
        ),
        "maraka": sorted(
            set(houses) & MARAKA_HOUSES
        ),
    }


def get_natural_nature(planet):
    """
    Return classical natural nature.

    This is deliberately separate from
    functional nature.
    """

    planet = normalize_planet(planet)

    if planet in NATURAL_BENEFICS:
        return "natural_benefic"

    if planet in NATURAL_MALEFICS:
        return "natural_malefic"

    return "neutral"


def get_functional_profile(
    ascendant_sign,
    planet
):
    """
    Build a structural functional profile.

    We do not collapse everything into one
    benefic/malefic label.
    """

    planet = normalize_planet(planet)

    lordships = get_house_lordships(
        ascendant_sign
    )

    owned_houses = lordships[planet]

    roles = classify_house_roles(
        owned_houses
    )

    natural_nature = get_natural_nature(
        planet
    )

    is_lagna_lord = 1 in owned_houses

    is_trikona_lord = bool(
        roles["trikona"]
    )

    is_kendra_lord = bool(
        roles["kendra"]
    )

    is_dusthana_lord = bool(
        roles["dusthana"]
    )

    is_trishadaya_lord = bool(
        roles["trishadaya"]
    )

    is_maraka_lord = bool(
        roles["maraka"]
    )

    # Classical structural indicators.
    # Do not treat these as an absolute final
    # benefic/malefic verdict.

    if is_lagna_lord:
        functional_role = "lagna_lord"

    elif is_trikona_lord and not is_dusthana_lord:
        functional_role = "trikona_lord"

    elif is_dusthana_lord:
        functional_role = "dusthana_lord"

    elif is_trishadaya_lord:
        functional_role = "trishadaya_lord"

    elif is_maraka_lord:
        functional_role = "maraka_lord"

    else:
        functional_role = "mixed"

    return {
        "planet": planet,
        "owned_houses": sorted(owned_houses),
        "house_roles": roles,
        "natural_nature": natural_nature,
        "is_lagna_lord": is_lagna_lord,
        "is_kendra_lord": is_kendra_lord,
        "is_trikona_lord": is_trikona_lord,
        "is_dusthana_lord": is_dusthana_lord,
        "is_trishadaya_lord": is_trishadaya_lord,
        "is_maraka_lord": is_maraka_lord,
        "primary_structural_role": functional_role,
    }


def build_functional_profiles(
    ascendant_sign
):
    """
    Build functional profiles for all seven
    classical planets.
    """

    return {
        planet: get_functional_profile(
            ascendant_sign,
            planet
        )
        for planet in PLANETS
    }
