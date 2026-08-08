"""
Yoga Strength & Affliction Engine
=================================

Evaluates the structural strength of already-detected Yogas.

This module does NOT:
- calculate planetary positions
- detect new Yogas
- calculate Dashas
- make predictive/client claims

It consumes:
    planets
    house_lords
    planet_house_mapping
    relationship_data
    aspect_data
    yoga_engine output
    grah_calculator output (when available)

Important:
The project knowledge base contains qualitative rules, not a validated
0-100 weighting model. Therefore this engine returns transparent factor
evidence and a conservative qualitative band instead of pretending that
an arbitrary numerical score is classical Jyotisha.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Iterable, Set


KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
TRISHADAYAS = {3, 6, 11}
MARAKAS = {2, 7}


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


def normalize_house(value: Any) -> Optional[int]:
    """Normalize a house value from either scalar or mapping form."""
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


def get_planet_data(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    data = planets.get(planet)
    return data if isinstance(data, dict) else {}


def get_sign(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
) -> Optional[str]:
    return get_planet_data(planet, planets).get("sign")


def get_dignity(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
    grah_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Prefer the canonical grah_calculator output when available.

    Falls back to sign-based dignity for core classical dignities.
    """
    if grah_data:
        candidate = grah_data.get(planet)

        if isinstance(candidate, dict):
            for key in (
                "dignity",
                "dignity_status",
                "planetary_dignity",
            ):
                value = candidate.get(key)
                if value:
                    return str(value).lower()

    sign = get_sign(planet, planets)

    if sign is None:
        return "unknown"

    if sign == EXALTATION_SIGNS.get(planet):
        return "exalted"

    if sign == DEBILITATION_SIGNS.get(planet):
        return "debilitated"

    if sign in OWN_SIGNS.get(planet, set()):
        return "own_sign"

    return "other"


def get_functional_roles(
    planet: str,
    relationship_data: Optional[Dict[str, Any]],
) -> Set[str]:
    """
    Read functional roles from planet_relationships.py v2.
    """
    if not relationship_data:
        return set()

    candidates = relationship_data.get(
        "functional_roles",
        {},
    )

    if isinstance(candidates, dict):
        record = candidates.get(planet)

        if isinstance(record, dict):
            roles = record.get("roles", [])
            return {
                str(role)
                for role in roles
            }

    return set()


def is_functional_benefic(
    planet: str,
    relationship_data: Optional[Dict[str, Any]],
) -> bool:
    roles = get_functional_roles(
        planet,
        relationship_data,
    )

    return bool(
        roles
        & {
            "lagna_lord",
            "kendra_lord",
            "trikona_lord",
            "kendra_trikona_lord",
        }
    )


def is_functional_malefic(
    planet: str,
    relationship_data: Optional[Dict[str, Any]],
) -> bool:
    roles = get_functional_roles(
        planet,
        relationship_data,
    )

    return bool(
        roles
        & {
            "dusthana_lord",
            "trishadaya_lord",
            "maraka_lord",
        }
    )


def get_natural_nature(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
    grah_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Prefer canonical grah_calculator output where available.

    Otherwise use the standard seven-planet baseline.
    """
    if grah_data:
        candidate = grah_data.get(planet)

        if isinstance(candidate, dict):
            for key in (
                "natural_nature",
                "nature",
                "natural_status",
            ):
                value = candidate.get(key)
                if value:
                    return str(value).lower()

    # Moon's natural classification is context-sensitive in many systems.
    # Keep it neutral here unless grah_calculator has already resolved it.
    if planet in {"Jupiter", "Venus", "Mercury", "Moon"}:
        return "benefic"

    if planet in {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}:
        return "malefic"

    return "unknown"


def get_aspecting_planets(
    target_planet: str,
    aspect_data: Optional[Dict[str, Any]],
) -> List[str]:
    if not aspect_data:
        return []

    results = []

    for item in aspect_data.get(
        "planet_to_planet",
        [],
    ):
        if item.get("target_planet") == target_planet:
            source = item.get("source_planet")

            if source and source not in results:
                results.append(source)

    return results


def get_conjunct_planets(
    target_planet: str,
    relationship_data: Optional[Dict[str, Any]],
    planets: Dict[str, Dict[str, Any]],
) -> List[str]:
    """
    Prefer relationship-engine Yuti data.
    Fall back to same-sign calculation.
    """
    results = []

    if relationship_data:
        for item in relationship_data.get(
            "planet_to_planet",
            [],
        ):
            a = item.get("planet_a")
            b = item.get("planet_b")

            same = item.get(
                "yuti",
                item.get("same_sign", False),
            )

            if not same:
                continue

            if a == target_planet and b:
                results.append(b)
            elif b == target_planet and a:
                results.append(a)

    if not results:
        target_sign = get_sign(
            target_planet,
            planets,
        )

        if target_sign:
            for planet, data in planets.items():
                if (
                    planet != target_planet
                    and isinstance(data, dict)
                    and data.get("sign") == target_sign
                ):
                    results.append(planet)

    return sorted(set(results))


def is_combust(
    planet: str,
    planet_data: Dict[str, Any],
) -> bool:
    """
    Read combustion only if an upstream calculator explicitly provides it.

    No combustion orb is invented here.
    """
    for key in (
        "combust",
        "combustion",
        "is_combust",
        "combust_status",
    ):
        value = planet_data.get(key)

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() in {
                "true",
                "yes",
                "combust",
                "ast",
                "burnt",
            }

    return False


def is_retrograde(
    planet_data: Dict[str, Any],
) -> bool:
    for key in (
        "retrograde",
        "is_retrograde",
        "vakri",
    ):
        value = planet_data.get(key)

        if isinstance(value, bool):
            return value

    return False


def append_unique(
    collection: List[Dict[str, Any]],
    factor: Dict[str, Any],
) -> None:
    key = (
        factor.get("type"),
        factor.get("planet"),
        factor.get("source_planet"),
        factor.get("house"),
        factor.get("description"),
    )

    existing = {
        (
            item.get("type"),
            item.get("planet"),
            item.get("source_planet"),
            item.get("house"),
            item.get("description"),
        )
        for item in collection
    }

    if key not in existing:
        collection.append(factor)


def evaluate_planet_strength(
    planet: str,
    planets: Dict[str, Dict[str, Any]],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
    grah_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate one participating planet.

    Returns evidence, not an arbitrary numerical strength score.
    """
    data = get_planet_data(
        planet,
        planets,
    )

    house = get_planet_house(
        planet,
        planet_house_mapping,
    )

    sign = data.get("sign")
    dignity = get_dignity(
        planet,
        planets,
        grah_data,
    )

    positive: List[Dict[str, Any]] = []
    negative: List[Dict[str, Any]] = []
    neutral: List[Dict[str, Any]] = []

    # ---------------------------------------------------------------
    # DIGNITY
    # ---------------------------------------------------------------

    if dignity == "exalted":
        positive.append({
            "type": "dignity",
            "planet": planet,
            "description": f"{planet} is exalted in {sign}.",
        })

    elif dignity in {
        "own",
        "own_sign",
        "swarashi",
    }:
        positive.append({
            "type": "dignity",
            "planet": planet,
            "description": f"{planet} is in its own sign {sign}.",
        })

    elif dignity in {
        "mool_trikona",
        "moola_trikona",
    }:
        positive.append({
            "type": "dignity",
            "planet": planet,
            "description": f"{planet} is in Mool Trikona.",
        })

    elif dignity == "debilitated":
        negative.append({
            "type": "dignity",
            "planet": planet,
            "description": f"{planet} is debilitated in {sign}.",
        })

    # ---------------------------------------------------------------
    # HOUSE PLACEMENT
    # ---------------------------------------------------------------

    if house in KENDRAS:
        positive.append({
            "type": "house",
            "planet": planet,
            "house": house,
            "description": (
                f"{planet} occupies Kendra house {house}."
            ),
        })

    if house in TRIKONAS:
        positive.append({
            "type": "house",
            "planet": planet,
            "house": house,
            "description": (
                f"{planet} occupies Trikona house {house}."
            ),
        })

    if house in DUSTHANAS:
        negative.append({
            "type": "house",
            "planet": planet,
            "house": house,
            "description": (
                f"{planet} occupies Dusthana house {house}."
            ),
        })

    # ---------------------------------------------------------------
    # FUNCTIONAL ROLE
    # ---------------------------------------------------------------

    if is_functional_benefic(
        planet,
        relationship_data,
    ):
        positive.append({
            "type": "functional_role",
            "planet": planet,
            "description": (
                f"{planet} has a functional-benefic role."
            ),
        })

    if is_functional_malefic(
        planet,
        relationship_data,
    ):
        negative.append({
            "type": "functional_role",
            "planet": planet,
            "description": (
                f"{planet} has a functional-malefic role."
            ),
        })

    # ---------------------------------------------------------------
    # NATURAL NATURE
    # ---------------------------------------------------------------

    nature = get_natural_nature(
        planet,
        planets,
        grah_data,
    )

    if nature == "benefic":
        positive.append({
            "type": "natural_nature",
            "planet": planet,
            "description": f"{planet} is treated as a natural benefic.",
        })

    elif nature == "malefic":
        negative.append({
            "type": "natural_nature",
            "planet": planet,
            "description": f"{planet} is treated as a natural malefic.",
        })

    # ---------------------------------------------------------------
    # COMBUSTION
    # ---------------------------------------------------------------

    if is_combust(planet, data):
        negative.append({
            "type": "combustion",
            "planet": planet,
            "description": (
                f"{planet} is marked combust by the upstream calculator."
            ),
        })

    # ---------------------------------------------------------------
    # RETROGRADE
    # ---------------------------------------------------------------

    if is_retrograde(data):
        neutral.append({
            "type": "retrograde",
            "planet": planet,
            "description": (
                f"{planet} is retrograde. Retrogression is retained "
                "as a separate modifying factor."
            ),
        })

    # ---------------------------------------------------------------
    # ASPECT AFFLICTION / SUPPORT
    # ---------------------------------------------------------------

    aspecting = get_aspecting_planets(
        planet,
        aspect_data,
    )

    for source in aspecting:

        source_nature = get_natural_nature(
            source,
            planets,
            grah_data,
        )

        if source_nature == "benefic":
            positive.append({
                "type": "benefic_aspect",
                "planet": planet,
                "source_planet": source,
                "description": (
                    f"{source} aspects {planet} and is treated "
                    "as a natural benefic."
                ),
            })

        elif source_nature == "malefic":
            negative.append({
                "type": "malefic_aspect",
                "planet": planet,
                "source_planet": source,
                "description": (
                    f"{source} aspects {planet} and is treated "
                    "as a natural malefic."
                ),
            })

    # ---------------------------------------------------------------
    # CONJUNCTION AFFLICTION / SUPPORT
    # ---------------------------------------------------------------

    conjunct = get_conjunct_planets(
        planet,
        relationship_data,
        planets,
    )

    for other in conjunct:

        other_nature = get_natural_nature(
            other,
            planets,
            grah_data,
        )

        if other_nature == "benefic":
            positive.append({
                "type": "benefic_conjunction",
                "planet": planet,
                "source_planet": other,
                "description": (
                    f"{other} is conjunct {planet} and is treated "
                    "as a natural benefic."
                ),
            })

        elif other_nature == "malefic":
            negative.append({
                "type": "malefic_conjunction",
                "planet": planet,
                "source_planet": other,
                "description": (
                    f"{other} is conjunct {planet} and is treated "
                    "as a natural malefic."
                ),
            })

    return {
        "planet": planet,
        "house": house,
        "sign": sign,
        "dignity": dignity,
        "positive_factors": positive,
        "negative_factors": negative,
        "neutral_factors": neutral,
    }


def detect_cancellation_factors(
    yoga: Dict[str, Any],
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Detect explicit structural cancellation/mitigation evidence.

    This is intentionally conservative.
    """
    factors: List[Dict[str, Any]] = []

    for planet in yoga.get("planets", []):

        house = get_planet_house(
            planet,
            planet_house_mapping,
        )

        # Benefic aspect is treated as mitigation evidence, not
        # automatic cancellation.
        for source in get_aspecting_planets(
            planet,
            aspect_data,
        ):
            source_nature = get_natural_nature(
                source,
                planets,
            )

            if source_nature == "benefic":
                factors.append({
                    "type": "mitigation",
                    "planet": planet,
                    "source_planet": source,
                    "description": (
                        f"Natural benefic {source} aspects {planet}; "
                        "this is recorded as mitigating evidence."
                    ),
                })

        # Own/exalted dignity can mitigate weakness.
        dignity = get_dignity(
            planet,
            planets,
        )

        if dignity in {
            "exalted",
            "own",
            "own_sign",
            "mool_trikona",
            "moola_trikona",
        }:
            factors.append({
                "type": "mitigation",
                "planet": planet,
                "house": house,
                "description": (
                    f"{planet} has supportive dignity: {dignity}."
                ),
            })

    return factors


def determine_strength_band(
    positive_count: int,
    negative_count: int,
    cancellation_count: int,
) -> str:
    """
    Conservative qualitative classification.

    This is a software status band, NOT a classical numerical strength score.
    """
    net = positive_count - negative_count

    if positive_count == 0 and negative_count == 0:
        return "undetermined"

    if net >= 3 and negative_count == 0:
        return "strong"

    if net >= 2:
        return "supportive"

    if negative_count > positive_count + 1:
        return "afflicted"

    if cancellation_count > 0 and negative_count >= positive_count:
        return "mixed_with_mitigation"

    if positive_count > negative_count:
        return "moderately_supportive"

    if positive_count == negative_count:
        return "mixed"

    return "weak"


def evaluate_yoga_strength(
    yoga: Dict[str, Any],
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
    grah_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate one Yoga record.
    """
    if not yoga.get("detected"):
        return {
            "yoga": yoga.get("yoga"),
            "detected": False,
            "strength_band": "not_detected",
            "positive_factors": [],
            "negative_factors": [],
            "cancellation_factors": [],
            "participating_planets": [],
        }

    participating_planets = list(
        dict.fromkeys(
            yoga.get("planets", [])
        )
    )

    positive: List[Dict[str, Any]] = []
    negative: List[Dict[str, Any]] = []
    neutral: List[Dict[str, Any]] = []

    planet_evaluations = []

    for planet in participating_planets:

        evaluation = evaluate_planet_strength(
            planet,
            planets,
            planet_house_mapping,
            relationship_data,
            aspect_data,
            grah_data,
        )

        planet_evaluations.append(evaluation)

        for factor in evaluation["positive_factors"]:
            append_unique(
                positive,
                factor,
            )

        for factor in evaluation["negative_factors"]:
            append_unique(
                negative,
                factor,
            )

        for factor in evaluation["neutral_factors"]:
            append_unique(
                neutral,
                factor,
            )

    cancellation = detect_cancellation_factors(
        yoga,
        planets,
        house_lords,
        planet_house_mapping,
        relationship_data,
        aspect_data,
    )

    strength_band = determine_strength_band(
        positive_count=len(positive),
        negative_count=len(negative),
        cancellation_count=len(cancellation),
    )

    return {
        "yoga": yoga.get("yoga"),
        "detected": True,
        "category": yoga.get("category"),
        "participating_planets": participating_planets,
        "houses_involved": yoga.get(
            "houses_involved",
            [],
        ),
        "mechanism": yoga.get("mechanism"),
        "strength_band": strength_band,
        "positive_factors": positive,
        "negative_factors": negative,
        "neutral_factors": neutral,
        "cancellation_factors": cancellation,
        "planet_evaluations": planet_evaluations,
        "rule_source": yoga.get(
            "rule_source",
            "project_rule",
        ),
    }


def build_yoga_strength_engine(
    yoga_data: Dict[str, Any],
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
    grah_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate all detected Yogas from yoga_engine.py.
    """
    source_yogas = yoga_data.get(
        "detected_yogas",
        yoga_data.get("yogas", []),
    )

    evaluated = []

    for yoga in source_yogas:

        if not yoga.get("detected"):
            continue

        evaluated.append(
            evaluate_yoga_strength(
                yoga,
                planets,
                house_lords,
                planet_house_mapping,
                relationship_data,
                aspect_data,
                grah_data,
            )
        )

    return {
        "engine": "yoga_strength",
        "version": "1.0",
        "yogas": evaluated,
        "count": len(evaluated),
    }


# ---------------------------------------------------------------------------
# COMPATIBILITY ALIAS
# ---------------------------------------------------------------------------

def calculate_yoga_strength(
    yoga_data: Dict[str, Any],
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Dict[str, Any],
    relationship_data: Optional[Dict[str, Any]] = None,
    aspect_data: Optional[Dict[str, Any]] = None,
    grah_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return build_yoga_strength_engine(
        yoga_data=yoga_data,
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=planet_house_mapping,
        relationship_data=relationship_data,
        aspect_data=aspect_data,
        grah_data=grah_data,
    )
