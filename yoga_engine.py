"""
Yoga Engine
===========

Structural Yoga detection for the Vedic astrology platform.

Design principles
-----------------
1. Do not recalculate planetary positions.
2. Do not recalculate D1 houses.
3. Consume existing:
      - planets
      - D1 whole-sign mapping
      - house lords
      - relationship data
      - aspect data
4. Return evidence, not final client interpretation.
5. Keep detection rules deterministic and auditable.

Primary supported Yoga families:
    - Raja Yoga
    - Dhana Yoga
    - Dharma-Karmadhipati Yoga
    - Vipareeta Raja Yoga
    - Neecha Bhanga indicators
    - Pancha Mahapurusha Yoga

The interpretation layer should be implemented separately.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Iterable

from yoga_strength import build_yoga_strength_engine


# ---------------------------------------------------------------------------
# HOUSE GROUPS
# ---------------------------------------------------------------------------

KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
DHANA_HOUSES = {2, 5, 9, 11}


# ---------------------------------------------------------------------------
# PLANETARY DIGNITY DATA
#
# Rahu/Ketu are intentionally excluded here because the project's own
# knowledge base records unresolved scholarly differences regarding their
# exaltation/debilitation signs.
# ---------------------------------------------------------------------------

EXALTATION_SIGNS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
}

DEBILITATION_SIGNS = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
}

OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
}


MAHAPURUSHA_YOGAS = {
    "Mars": {
        "yoga": "Ruchaka Mahapurusha Yoga",
        "own_signs": {"Aries", "Scorpio"},
        "exaltation_sign": "Capricorn",
    },
    "Mercury": {
        "yoga": "Bhadra Mahapurusha Yoga",
        "own_signs": {"Gemini", "Virgo"},
        "exaltation_sign": "Virgo",
    },
    "Jupiter": {
        "yoga": "Hamsa Mahapurusha Yoga",
        "own_signs": {"Sagittarius", "Pisces"},
        "exaltation_sign": "Cancer",
    },
    "Venus": {
        "yoga": "Malavya Mahapurusha Yoga",
        "own_signs": {"Taurus", "Libra"},
        "exaltation_sign": "Pisces",
    },
    "Saturn": {
        "yoga": "Sasa Mahapurusha Yoga",
        "own_signs": {"Capricorn", "Aquarius"},
        "exaltation_sign": "Libra",
    },
}


# ---------------------------------------------------------------------------
# BASIC NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_house(value: Any) -> Optional[int]:
    """
    Accept:
        5
        {"house": 5}
        {"house_number": 5}
    """
    if isinstance(value, dict):
        value = value.get("house", value.get("house_number"))

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_planet_house(
    planet: str,
    planet_house_mapping: Dict[str, Any],
) -> Optional[int]:
    return normalize_house(
        planet_house_mapping.get(planet)
    )


def get_planet_sign(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
) -> Optional[str]:
    data = planets.get(planet)

    if not isinstance(data, dict):
        return None

    return data.get("sign")


def get_planet_longitude(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
) -> Optional[float]:
    data = planets.get(planet)

    if not isinstance(data, dict):
        return None

    longitude = data.get("longitude")

    if longitude is None:
        return None

    try:
        return float(longitude)
    except (TypeError, ValueError):
        return None


def get_house_lord(
    house: int,
    house_lords: Dict[int, str],
) -> Optional[str]:
    return house_lords.get(house)


def get_owned_houses(
    planet: str,
    house_lords: Dict[int, str],
) -> List[int]:
    return sorted(
        house
        for house, lord in house_lords.items()
        if lord == planet
    )


# ---------------------------------------------------------------------------
# RELATIONSHIP HELPERS
# ---------------------------------------------------------------------------

def same_sign(
    planet_a: str,
    planet_b: str,
    planets: Dict[str, Dict[str, Any]],
) -> bool:
    sign_a = get_planet_sign(planet_a, planets)
    sign_b = get_planet_sign(planet_b, planets)

    return (
        sign_a is not None
        and sign_b is not None
        and sign_a == sign_b
    )


def find_planet_relationship(
    planet_a: str,
    planet_b: str,
    relationship_data: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if not relationship_data:
        return None

    relationships = relationship_data.get(
        "planet_to_planet",
        []
    )

    for item in relationships:
        a = item.get("planet_a")
        b = item.get("planet_b")

        if {a, b} == {planet_a, planet_b}:
            return item

    return None


def has_yuti(
    planet_a: str,
    planet_b: str,
    planets: Dict[str, Dict[str, Any]],
    relationship_data: Optional[Dict[str, Any]] = None,
) -> bool:
    relationship = find_planet_relationship(
        planet_a,
        planet_b,
        relationship_data,
    )

    if relationship is not None:
        return bool(
            relationship.get(
                "yuti",
                relationship.get("same_sign", False),
            )
        )

    return same_sign(
        planet_a,
        planet_b,
        planets,
    )


def has_aspect(
    source_planet: str,
    target_planet: str,
    aspect_data: Optional[Dict[str, Any]],
) -> bool:
    """
    Consume the existing planet_aspects engine.

    No aspect mathematics is repeated here.
    """

    if not aspect_data:
        return False

    relationships = aspect_data.get(
        "planet_to_planet",
        []
    )

    for item in relationships:
        if (
            item.get("source_planet") == source_planet
            and item.get("target_planet") == target_planet
        ):
            return True

    return False


def planets_related(
    planet_a: str,
    planet_b: str,
    planets: Dict[str, Dict[str, Any]],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Determine structural relationship between two planets.

    Priority:
        conjunction
        aspect
        mutual aspect
    """

    yuti = has_yuti(
        planet_a,
        planet_b,
        planets,
        relationship_data,
    )

    a_to_b = has_aspect(
        planet_a,
        planet_b,
        aspect_data,
    )

    b_to_a = has_aspect(
        planet_b,
        planet_a,
        aspect_data,
    )

    return {
        "yuti": yuti,
        "a_aspects_b": a_to_b,
        "b_aspects_a": b_to_a,
        "mutual_aspect": a_to_b and b_to_a,
        "related": yuti or a_to_b or b_to_a,
    }


# ---------------------------------------------------------------------------
# EVIDENCE BUILDER
# ---------------------------------------------------------------------------

def yoga_record(
    name: str,
    detected: bool,
    *,
    category: str,
    planets: Optional[Iterable[str]] = None,
    houses: Optional[Iterable[int]] = None,
    mechanism: Optional[str] = None,
    evidence: Optional[List[str]] = None,
    rule_source: str = "project_rule",
) -> Dict[str, Any]:
    """
    Standard Yoga output.

    This format is deliberately AI-consultation friendly.
    """

    return {
        "yoga": name,
        "detected": bool(detected),
        "category": category,
        "planets": list(planets or []),
        "houses_involved": list(houses or []),
        "mechanism": mechanism,
        "evidence": list(evidence or []),
        "rule_source": rule_source,
    }


# ---------------------------------------------------------------------------
# RAJA YOGA
# ---------------------------------------------------------------------------

def detect_raja_yoga(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:

    results = []

    kendra_lords = {
        house: house_lords.get(house)
        for house in KENDRAS
        if house_lords.get(house)
    }

    trikona_lords = {
        house: house_lords.get(house)
        for house in TRIKONAS
        if house_lords.get(house)
    }

    checked = set()

    for kendra_house, kendra_lord in kendra_lords.items():
        for trikona_house, trikona_lord in trikona_lords.items():

            if not kendra_lord or not trikona_lord:
                continue

            if kendra_lord == trikona_lord:
                continue

            pair = tuple(
                sorted(
                    (kendra_lord, trikona_lord)
                )
            )

            if pair in checked:
                continue

            checked.add(pair)

            relation = planets_related(
                kendra_lord,
                trikona_lord,
                planets,
                relationship_data,
                aspect_data,
            )

            if not relation["related"]:
                continue

            kendra_lord_house = get_planet_house(
                kendra_lord,
                planet_house_mapping,
            )

            trikona_lord_house = get_planet_house(
                trikona_lord,
                planet_house_mapping,
            )

            mechanisms = []

            if relation["yuti"]:
                mechanisms.append("yuti")

            if relation["a_aspects_b"]:
                mechanisms.append(
                    f"{kendra_lord}_aspects_{trikona_lord}"
                )

            if relation["b_aspects_a"]:
                mechanisms.append(
                    f"{trikona_lord}_aspects_{kendra_lord}"
                )

            results.append(
                yoga_record(
                    "Raja Yoga",
                    True,
                    category="raja",
                    planets=pair,
                    houses=[
                        kendra_house,
                        trikona_house,
                    ],
                    mechanism="relationship",
                    evidence=[
                        (
                            f"{kendra_house}th house lord "
                            f"{kendra_lord} is related to "
                            f"{trikona_house}th house lord "
                            f"{trikona_lord}."
                        ),
                        f"Relationship mechanism: {', '.join(mechanisms)}.",
                        (
                            f"{kendra_lord} occupies house "
                            f"{kendra_lord_house}."
                        )
                        if kendra_lord_house
                        else "",
                        (
                            f"{trikona_lord} occupies house "
                            f"{trikona_lord_house}."
                        )
                        if trikona_lord_house
                        else "",
                    ],
                    rule_source="structural_kendra_trikona_relationship",
                )
            )

    return results


# ---------------------------------------------------------------------------
# DHANA YOGA
# ---------------------------------------------------------------------------

def detect_dhana_yoga(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:

    results = []

    relevant_houses = sorted(DHANA_HOUSES)

    for index, house_a in enumerate(relevant_houses):
        lord_a = house_lords.get(house_a)

        if not lord_a:
            continue

        for house_b in relevant_houses[index + 1:]:
            lord_b = house_lords.get(house_b)

            if not lord_b or lord_a == lord_b:
                continue

            relation = planets_related(
                lord_a,
                lord_b,
                planets,
                relationship_data,
                aspect_data,
            )

            if not relation["related"]:
                continue

            mechanisms = []

            if relation["yuti"]:
                mechanisms.append("yuti")

            if relation["a_aspects_b"]:
                mechanisms.append(
                    f"{lord_a}_aspects_{lord_b}"
                )

            if relation["b_aspects_a"]:
                mechanisms.append(
                    f"{lord_b}_aspects_{lord_a}"
                )

            results.append(
                yoga_record(
                    "Dhana Yoga",
                    True,
                    category="wealth",
                    planets=[lord_a, lord_b],
                    houses=[house_a, house_b],
                    mechanism="relationship",
                    evidence=[
                        (
                            f"{house_a}th and {house_b}th "
                            f"house lords are related."
                        ),
                        f"Relationship: {', '.join(mechanisms)}.",
                    ],
                    rule_source="structural_dhana_house_relationship",
                )
            )

    return results


# ---------------------------------------------------------------------------
# DHARMA-KARMADHIPATI YOGA
# ---------------------------------------------------------------------------

def detect_dharma_karmadhipati_yoga(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:

    ninth_lord = house_lords.get(9)
    tenth_lord = house_lords.get(10)

    if not ninth_lord or not tenth_lord:
        return []

    if ninth_lord == tenth_lord:
        return []

    relation = planets_related(
        ninth_lord,
        tenth_lord,
        planets,
        relationship_data,
        aspect_data,
    )

    if not relation["related"]:
        return []

    mechanisms = []

    if relation["yuti"]:
        mechanisms.append("yuti")

    if relation["a_aspects_b"]:
        mechanisms.append(
            f"{ninth_lord}_aspects_{tenth_lord}"
        )

    if relation["b_aspects_a"]:
        mechanisms.append(
            f"{tenth_lord}_aspects_{ninth_lord}"
        )

    return [
        yoga_record(
            "Dharma-Karmadhipati Yoga",
            True,
            category="raja",
            planets=[
                ninth_lord,
                tenth_lord,
            ],
            houses=[9, 10],
            mechanism="relationship",
            evidence=[
                (
                    f"9th lord {ninth_lord} is related to "
                    f"10th lord {tenth_lord}."
                ),
                f"Relationship: {', '.join(mechanisms)}.",
            ],
            rule_source="structural_9th_10th_lord_relationship",
        )
    ]


# ---------------------------------------------------------------------------
# VIPAREETA RAJA YOGA
# ---------------------------------------------------------------------------

def detect_vipareeta_raja_yoga(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:

    results = []

    dusthana_houses = [6, 8, 12]

    for source_house in dusthana_houses:

        lord = house_lords.get(source_house)

        if not lord:
            continue

        lord_house = get_planet_house(
            lord,
            planet_house_mapping,
        )

        if lord_house not in DUSTHANAS:
            continue

        if lord_house == source_house:
            continue

        # Strict project rule:
        # the Dusthana lord must not be associated with another
        # house lord through conjunction/aspect.
        other_house_lords = set(
            house_lords.values()
        )

        associated_house_lords = []

        for other_lord in other_house_lords:

            if other_lord == lord:
                continue

            if not isinstance(other_lord, str):
                continue

            if has_yuti(
                lord,
                other_lord,
                planets,
            ):
                associated_house_lords.append(
                    other_lord
                )

        if associated_house_lords:
            continue

        results.append(
            yoga_record(
                "Vipareeta Raja Yoga",
                True,
                category="vipareeta",
                planets=[lord],
                houses=[
                    source_house,
                    lord_house,
                ],
                mechanism="dusthana_lord_in_another_dusthana",
                evidence=[
                    (
                        f"{source_house}th lord {lord} "
                        f"is placed in the {lord_house}th house."
                    ),
                    (
                        "No conjunction with another house lord "
                        "was found."
                    ),
                ],
                rule_source="Masterfile_Chapter_5",
            )
        )

    return results


# ---------------------------------------------------------------------------
# NEECHA BHANGA INDICATORS
# ---------------------------------------------------------------------------

def detect_neecha_bhanga(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:

    results = []

    for planet, debilitation_sign in DEBILITATION_SIGNS.items():

        if planet not in planets:
            continue

        sign = get_planet_sign(
            planet,
            planets,
        )

        if sign != debilitation_sign:
            continue

        cancellation_factors = []

        # Factor 1:
        # Lord of the debilitation sign placed in a Kendra.
        debilitation_sign_lord = None

        sign_lords = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter",
        }

        debilitation_sign_lord = sign_lords.get(
            debilitation_sign
        )

        lord_house = get_planet_house(
            debilitation_sign_lord,
            planet_house_mapping,
        )

        if lord_house in KENDRAS:
            cancellation_factors.append({
                "factor": "debilitation_sign_lord_in_kendra",
                "planet": debilitation_sign_lord,
                "house": lord_house,
            })

        # Factor 2:
        # Lord of the exaltation sign placed in a Kendra.
        exaltation_sign = EXALTATION_SIGNS.get(planet)

        exaltation_sign_lord = (
            sign_lords.get(exaltation_sign)
            if exaltation_sign
            else None
        )

        exaltation_lord_house = get_planet_house(
            exaltation_sign_lord,
            planet_house_mapping,
        )

        if exaltation_lord_house in KENDRAS:
            cancellation_factors.append({
                "factor": "exaltation_sign_lord_in_kendra",
                "planet": exaltation_sign_lord,
                "house": exaltation_lord_house,
            })

        if not cancellation_factors:
            continue

        results.append(
            yoga_record(
                "Neecha Bhanga Indicator",
                True,
                category="dignity",
                planets=[
                    planet,
                    *[
                        item["planet"]
                        for item in cancellation_factors
                        if item.get("planet")
                    ],
                ],
                houses=[
                    item["house"]
                    for item in cancellation_factors
                    if item.get("house")
                ],
                mechanism="debilitation_cancellation_factor",
                evidence=[
                    (
                        f"{planet} is debilitated in "
                        f"{debilitation_sign}."
                    ),
                    *[
                        (
                            f"Cancellation factor: "
                            f"{item['factor']} — "
                            f"{item['planet']} in house "
                            f"{item['house']}."
                        )
                        for item in cancellation_factors
                    ],
                ],
                rule_source="structural_neecha_bhanga_indicator",
            )
        )

    return results


# ---------------------------------------------------------------------------
# PANCHA MAHAPURUSHA YOGA
# ---------------------------------------------------------------------------

def detect_pancha_mahapurusha(
    planets: Dict[str, Dict[str, Any]],
    planet_house_mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:

    results = []

    for planet, definition in MAHAPURUSHA_YOGAS.items():

        if planet not in planets:
            continue

        house = get_planet_house(
            planet,
            planet_house_mapping,
        )

        if house not in KENDRAS:
            continue

        sign = get_planet_sign(
            planet,
            planets,
        )

        if sign is None:
            continue

        dignity = None

        if sign in definition["own_signs"]:
            dignity = "own_sign"

        elif sign == definition["exaltation_sign"]:
            dignity = "exalted"

        if dignity is None:
            continue

        results.append(
            yoga_record(
                definition["yoga"],
                True,
                category="mahapurusha",
                planets=[planet],
                houses=[house],
                mechanism=dignity,
                evidence=[
                    (
                        f"{planet} occupies Kendra house "
                        f"{house}."
                    ),
                    (
                        f"{planet} is in {dignity} condition "
                        f"in {sign}."
                    ),
                ],
                rule_source="structural_mahapurusha_rule",
            )
        )

    return results


# ---------------------------------------------------------------------------
# MASTER YOGA ENGINE
# ---------------------------------------------------------------------------

def build_yoga_engine(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    yogas: List[Dict[str, Any]] = []

    yogas.extend(
        detect_raja_yoga(
            planets,
            house_lords,
            planet_house_mapping,
            relationship_data,
            aspect_data,
        )
    )

    yogas.extend(
        detect_dhana_yoga(
            planets,
            house_lords,
            relationship_data,
            aspect_data,
        )
    )

    yogas.extend(
        detect_dharma_karmadhipati_yoga(
            planets,
            house_lords,
            relationship_data,
            aspect_data,
        )
    )

    yogas.extend(
        detect_vipareeta_raja_yoga(
            planets,
            house_lords,
            planet_house_mapping,
        )
    )

    yogas.extend(
        detect_neecha_bhanga(
            planets,
            house_lords,
            planet_house_mapping,
        )
    )

    yogas.extend(
        detect_pancha_mahapurusha(
            planets,
            planet_house_mapping,
        )
    )

    detected = [
        yoga
        for yoga in yogas
        if yoga["detected"]
    ]

    return {
        "engine": "yoga_engine",
        "version": "1.0",
        "yogas": yogas,
        "detected_yogas": detected,
        "count": len(detected),
    }




# ---------------------------------------------------------------------------
# COMPLETE YOGA ANALYSIS
# ---------------------------------------------------------------------------

def build_complete_yoga_analysis(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
    grah_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run Yoga detection first, then evaluate the strength/affliction layer.

    This is the integration entry point for the Yoga subsystem.

    Pipeline:
        build_yoga_engine()
            ->
        build_yoga_strength_engine()
    """

    yoga_data = build_yoga_engine(
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=planet_house_mapping,
        relationship_data=relationship_data,
        aspect_data=aspect_data,
    )

    strength_data = build_yoga_strength_engine(
        yoga_data=yoga_data,
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=planet_house_mapping,
        relationship_data=relationship_data,
        aspect_data=aspect_data,
        grah_data=grah_data,
    )

    return {
        "engine": "complete_yoga_analysis",
        "version": "1.0",
        "yoga_detection": yoga_data,
        "yoga_strength": strength_data,
        "detected_count": yoga_data.get("count", 0),
        "evaluated_count": strength_data.get("count", 0),
    }


# ---------------------------------------------------------------------------
# COMPATIBILITY ALIAS
# ---------------------------------------------------------------------------

def calculate_yogas(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Public compatibility function.
    """
    return build_yoga_engine(
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=planet_house_mapping,
        relationship_data=relationship_data,
        aspect_data=aspect_data,
    )
