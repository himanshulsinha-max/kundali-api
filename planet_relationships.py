"""
Planet Relationship Engine - v2
===============================

Builds the relationship data layer required by the Yoga and interpretation
engines.  This module calculates relationships; it does NOT decide whether
a Yoga exists.

Responsibilities
----------------
- Natural planetary Maitri
- Functional house-lord classification
- Planet-to-planet same-sign association (Yuti/association layer)
- Degree separation
- Planet -> sign lord / dispositor
- Dispositor chains
- Planet -> house / house lord
- House-lord -> house-lord relationships
- Parivartana (sign exchange)
- Dusthana / Trishadaya / Maraka / Badhakesh metadata
- Query helpers for later Yoga detection

Design notes
------------
1. Whole-sign D1 is the base house framework.
2. Same-sign association is deliberately distinct from exact degree proximity.
3. Graha Drishti/aspects are NOT calculated here; they belong in the aspect
   engine.
4. Yoga detection is NOT performed here.
5. Rahu/Ketu Maitri is configurable because the supplied source material
   contains differing treatment across traditions.
"""

from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# PLANETS
# ---------------------------------------------------------------------------

PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]


# ---------------------------------------------------------------------------
# RELATIONSHIP CONFIGURATION
# ---------------------------------------------------------------------------

# The Masterfile supplied with the project gives Rahu/Ketu a specific
# relationship treatment. Keep this configurable so another classical school
# can be selected later without rewriting the engine.
RELATIONSHIP_TRADITION = "masterfile"


NATURAL_RELATIONSHIPS_MASTERFILE = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "enemies": ["Venus", "Saturn"],
        "neutrals": ["Mercury"],
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "enemies": [],
        "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "enemies": ["Mercury"],
        "neutrals": ["Venus", "Saturn"],
    },
    "Mercury": {
        "friends": ["Sun", "Venus"],
        "enemies": ["Moon"],
        "neutrals": ["Mars", "Jupiter", "Saturn"],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "enemies": ["Mercury", "Venus"],
        "neutrals": ["Saturn"],
    },
    "Venus": {
        "friends": ["Mercury", "Saturn"],
        "enemies": ["Sun", "Moon"],
        "neutrals": ["Mars", "Jupiter"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutrals": ["Jupiter"],
    },
    "Rahu": {
        "friends": ["Venus", "Saturn"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutrals": [],
    },
    "Ketu": {
        "friends": ["Venus", "Saturn"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutrals": [],
    },
}


NATURAL_RELATIONSHIPS_UNSPECIFIED_NODES = {
    **{
        planet: data.copy()
        for planet, data in NATURAL_RELATIONSHIPS_MASTERFILE.items()
        if planet not in {"Rahu", "Ketu"}
    },
    "Rahu": {"friends": [], "enemies": [], "neutrals": []},
    "Ketu": {"friends": [], "enemies": [], "neutrals": []},
}


RELATIONSHIP_TABLES = {
    "masterfile": NATURAL_RELATIONSHIPS_MASTERFILE,
    "nodes_unspecified": NATURAL_RELATIONSHIPS_UNSPECIFIED_NODES,
}

NATURAL_RELATIONSHIPS = RELATIONSHIP_TABLES[RELATIONSHIP_TRADITION]


# ---------------------------------------------------------------------------
# SIGN LORDS
# ---------------------------------------------------------------------------

SIGN_LORDS = {
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

SIGN_LORDS_BY_INDEX = {
    0: "Mars",
    1: "Venus",
    2: "Mercury",
    3: "Moon",
    4: "Sun",
    5: "Mercury",
    6: "Venus",
    7: "Mars",
    8: "Jupiter",
    9: "Saturn",
    10: "Saturn",
    11: "Jupiter",
}

SIGN_NAMES_BY_INDEX = {
    index: sign for index, sign in enumerate(SIGN_LORDS.keys())
}


# ---------------------------------------------------------------------------
# HOUSE GROUPS
# ---------------------------------------------------------------------------

KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
TRISHADAYAS = {3, 6, 11}
MARAKAS = {2, 7}
UPACHAYAS = {3, 6, 10, 11}


# ---------------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------------

def get_sign_lord(sign: Optional[str]) -> Optional[str]:
    """Return the lord of a zodiac sign."""
    if sign is None:
        return None
    return SIGN_LORDS.get(sign)


def get_sign_lord_by_index(sign_index: Optional[int]) -> Optional[str]:
    """Return sign lord using the 0-11 sign index."""
    if sign_index is None:
        return None
    return SIGN_LORDS_BY_INDEX.get(sign_index)


def get_planet_sign_index(planet_data: Dict[str, Any]) -> Optional[int]:
    value = planet_data.get("sign_index")
    return value if isinstance(value, int) else None


def get_planet_sign(planet_data: Dict[str, Any]) -> Optional[str]:
    sign = planet_data.get("sign")
    if sign:
        return sign
    sign_index = get_planet_sign_index(planet_data)
    return SIGN_NAMES_BY_INDEX.get(sign_index)


def natural_relationship(planet_a: str, planet_b: str) -> str:
    """
    Return the natural relationship of planet_a toward planet_b.

    Possible values:
        friend, enemy, neutral, unknown, same_planet
    """
    if planet_a == planet_b:
        return "same_planet"

    data = NATURAL_RELATIONSHIPS.get(planet_a)
    if not data:
        return "unknown"

    if planet_b in data["friends"]:
        return "friend"
    if planet_b in data["enemies"]:
        return "enemy"
    if planet_b in data["neutrals"]:
        return "neutral"
    return "unknown"


def house_group(house: Optional[int]) -> Optional[str]:
    """Classify a house for relationship/Yoga queries."""
    if house is None:
        return None
    if house in KENDRAS:
        return "kendra"
    if house in TRIKONAS:
        return "trikona"
    if house in DUSTHANAS:
        return "dusthana"
    if house in TRISHADAYAS:
        return "trishadaya"
    if house in MARAKAS:
        return "maraka"
    if house in UPACHAYAS:
        return "upachaya"
    return "other"


def normalize_house_mapping_value(value: Any) -> Optional[int]:
    """Accept either an integer house or the existing {'house': N} format."""
    if isinstance(value, dict):
        value = value.get("house")
    return value if isinstance(value, int) else None


# ---------------------------------------------------------------------------
# YUTI / SAME-SIGN ASSOCIATION
# ---------------------------------------------------------------------------

def planets_conjunct(
    planet_a: Dict[str, Any],
    planet_b: Dict[str, Any],
) -> bool:
    """
    Determine whole-sign conjunction/association.

    Exact degree-based conjunction is intentionally NOT used as the definition
    here. Degree separation is returned separately for later precision rules.
    """
    sign_a = get_planet_sign_index(planet_a)
    sign_b = get_planet_sign_index(planet_b)

    if sign_a is not None and sign_b is not None:
        return sign_a == sign_b

    return get_planet_sign(planet_a) is not None and get_planet_sign(planet_a) == get_planet_sign(planet_b)


def degree_separation(
    planet_a: Dict[str, Any],
    planet_b: Dict[str, Any],
) -> Optional[float]:
    """Calculate the minimum absolute longitudinal separation in degrees."""
    longitude_a = planet_a.get("longitude")
    longitude_b = planet_b.get("longitude")

    if longitude_a is None or longitude_b is None:
        return None

    difference = abs(float(longitude_a) - float(longitude_b))
    if difference > 180:
        difference = 360 - difference

    return round(difference, 6)


def build_planet_relationship(
    planet_a_name: str,
    planet_a: Dict[str, Any],
    planet_b_name: str,
    planet_b: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a normalized relationship record between two planets."""
    separation = degree_separation(planet_a, planet_b)
    same_sign = planets_conjunct(planet_a, planet_b)

    return {
        "planet_a": planet_a_name,
        "planet_b": planet_b_name,
        "same_sign": same_sign,
        "yuti": same_sign,
        "degree_separation": separation,
        "natural_relationship": natural_relationship(planet_a_name, planet_b_name),
        "reverse_natural_relationship": natural_relationship(planet_b_name, planet_a_name),
    }


def build_planet_to_planet_relationships(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build unique pairwise relationships."""
    available_planets = [planet for planet in PLANETS if planet in planets]
    relationships: List[Dict[str, Any]] = []

    for i, planet_a_name in enumerate(available_planets):
        for planet_b_name in available_planets[i + 1:]:
            relationships.append(
                build_planet_relationship(
                    planet_a_name,
                    planets[planet_a_name],
                    planet_b_name,
                    planets[planet_b_name],
                )
            )

    return relationships


# ---------------------------------------------------------------------------
# PLANET -> SIGN LORD / DISPOSITOR
# ---------------------------------------------------------------------------

def get_planet_sign_lord(
    planet_data: Dict[str, Any],
) -> Optional[str]:
    sign = get_planet_sign(planet_data)
    return get_sign_lord(sign)


def build_planet_sign_lord_relationship(
    planet_name: str,
    planet_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Determine the relationship between a planet and its sign lord."""
    sign = get_planet_sign(planet_data)
    sign_index = get_planet_sign_index(planet_data)
    lord = get_planet_sign_lord(planet_data)

    return {
        "planet": planet_name,
        "sign": sign,
        "sign_index": sign_index,
        "sign_lord": lord,
        "dispositor": lord,
        "natural_relationship": (
            natural_relationship(planet_name, lord) if lord else "unknown"
        ),
        "same_planet": planet_name == lord if lord else False,
    }


def build_all_sign_lord_relationships(
    planets: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build sign-lord/dispositor relationships for all available planets."""
    return [
        build_planet_sign_lord_relationship(planet_name, planets[planet_name])
        for planet_name in PLANETS
        if planet_name in planets
    ]


def get_dispositor(
    planet_name: str,
    planets: Dict[str, Dict[str, Any]],
) -> Optional[str]:
    """Return the immediate dispositor of a planet."""
    planet_data = planets.get(planet_name)
    if not planet_data:
        return None
    return get_planet_sign_lord(planet_data)


def get_dispositor_chain(
    planet_name: str,
    planets: Dict[str, Dict[str, Any]],
    max_depth: int = 12,
) -> List[str]:
    """
    Follow dispositor links until a terminal planet or a cycle is reached.

    The starting planet is included. Cycles are represented once and then
    stopped to prevent infinite loops (e.g. mutual sign exchange).
    """
    chain: List[str] = []
    seen: Set[str] = set()
    current = planet_name

    while current and len(chain) < max_depth:
        if current in seen:
            break

        seen.add(current)
        chain.append(current)
        current = get_dispositor(current, planets)

    return chain


# ---------------------------------------------------------------------------
# PLANET -> HOUSE / HOUSE LORD
# ---------------------------------------------------------------------------

def build_planet_house_relationships(
    planets: Dict[str, Dict[str, Any]],
    planet_house_mapping: Dict[str, Any],
    house_lords: Dict[int, str],
) -> List[Dict[str, Any]]:
    """Connect each planet with its house and that house's lord."""
    relationships: List[Dict[str, Any]] = []

    for planet_name, planet_data in planets.items():
        house_number = normalize_house_mapping_value(
            planet_house_mapping.get(planet_name)
        )
        if house_number is None:
            continue

        house_lord = house_lords.get(house_number)
        relationships.append({
            "planet": planet_name,
            "house": house_number,
            "house_group": house_group(house_number),
            "house_lord": house_lord,
            "planet_is_house_lord": planet_name == house_lord,
            "natural_relationship": (
                natural_relationship(planet_name, house_lord)
                if house_lord
                else "unknown"
            ),
            "sign": get_planet_sign(planet_data),
            "sign_index": get_planet_sign_index(planet_data),
            "dispositor": get_planet_sign_lord(planet_data),
        })

    return relationships


def build_house_lord_relationships(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Build the relationship of each house lord to the other house lords.

    This is intentionally structural data. The Yoga engine decides whether a
    particular relationship constitutes a Raja/Dhana/etc. Yoga.
    """
    relationships: List[Dict[str, Any]] = []

    for house_number, lord in sorted(house_lords.items()):
        lord_house = None
        if planet_house_mapping and lord in planet_house_mapping:
            lord_house = normalize_house_mapping_value(
                planet_house_mapping[lord]
            )

        for other_house, other_lord in sorted(house_lords.items()):
            if house_number == other_house:
                continue

            relationships.append({
                "house_a": house_number,
                "lord_a": lord,
                "house_a_group": house_group(house_number),
                "lord_a_house": lord_house,
                "house_b": other_house,
                "lord_b": other_lord,
                "house_b_group": house_group(other_house),
                "lord_relationship": natural_relationship(lord, other_lord),
                "same_lord": lord == other_lord,
            })

    return relationships


# ---------------------------------------------------------------------------
# FUNCTIONAL PLANET CLASSIFICATION
# ---------------------------------------------------------------------------

def get_houses_owned_by_planet(
    planet: str,
    house_lords: Dict[int, str],
) -> List[int]:
    """Return all houses owned by the specified planet in the supplied D1."""
    return sorted(
        house for house, lord in house_lords.items() if lord == planet
    )


def classify_functional_role(
    planet: str,
    owned_houses: List[int],
) -> Dict[str, Any]:
    """Return transparent house-based functional classifications."""
    owned = set(owned_houses)

    roles: List[str] = []
    if 1 in owned:
        roles.append("lagna_lord")
    if owned & KENDRAS:
        roles.append("kendra_lord")
    if owned & TRIKONAS:
        roles.append("trikona_lord")
    if owned & DUSTHANAS:
        roles.append("dusthana_lord")
    if owned & TRISHADAYAS:
        roles.append("trishadaya_lord")
    if owned & MARAKAS:
        roles.append("maraka_lord")

    # A planet owning both a Kendra and Trikona is structurally important for
    # Raja-yoga analysis, but this function deliberately does not declare a
    # Yoga. That decision belongs to yoga_engine.py.
    if owned & KENDRAS and owned & TRIKONAS:
        roles.append("kendra_trikona_lord")

    return {
        "planet": planet,
        "owned_houses": owned_houses,
        "roles": roles,
        "is_kendra_lord": bool(owned & KENDRAS),
        "is_trikona_lord": bool(owned & TRIKONAS),
        "is_dusthana_lord": bool(owned & DUSTHANAS),
        "is_trishadaya_lord": bool(owned & TRISHADAYAS),
        "is_maraka_lord": bool(owned & MARAKAS),
        "is_kendra_trikona_lord": bool(owned & KENDRAS and owned & TRIKONAS),
    }


def build_functional_planet_relationships(
    house_lords: Dict[int, str],
) -> List[Dict[str, Any]]:
    """Build functional classifications for every planet acting as a lord."""
    return [
        classify_functional_role(
            planet,
            get_houses_owned_by_planet(planet, house_lords),
        )
        for planet in PLANETS
        if planet in set(house_lords.values())
    ]


# ---------------------------------------------------------------------------
# BADHAKESH
# ---------------------------------------------------------------------------

MOVABLE_LAGNAS = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_LAGNAS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
DUAL_LAGNAS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}


def get_badhaka_house(lagna_sign: Optional[str]) -> Optional[int]:
    """Return the Badhaka house according to Lagna modality."""
    if lagna_sign in MOVABLE_LAGNAS:
        return 11
    if lagna_sign in FIXED_LAGNAS:
        return 9
    if lagna_sign in DUAL_LAGNAS:
        return 7
    return None


def get_badhakesh(
    lagna_sign: Optional[str],
    house_lords: Dict[int, str],
) -> Optional[str]:
    """Return the lord of the Badhaka house for the given Lagna."""
    badhaka_house = get_badhaka_house(lagna_sign)
    if badhaka_house is None:
        return None
    return house_lords.get(badhaka_house)


def build_badhakesh_relationship(
    lagna_sign: Optional[str],
    house_lords: Dict[int, str],
) -> Dict[str, Any]:
    badhaka_house = get_badhaka_house(lagna_sign)
    badhakesh = get_badhakesh(lagna_sign, house_lords)
    return {
        "lagna_sign": lagna_sign,
        "badhaka_house": badhaka_house,
        "badhakesh": badhakesh,
    }


# ---------------------------------------------------------------------------
# PARIVARTANA / SIGN EXCHANGE
# ---------------------------------------------------------------------------

def detect_parivartana_yogas(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Dict[int, str],
    planet_house_mapping: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Detect mutual sign exchange between two house lords.

    Condition:
        Lord A occupies a sign owned by Lord B, and
        Lord B occupies a sign owned by Lord A.

    The result is structural metadata; Yoga interpretation belongs elsewhere.
    """
    exchanges: List[Dict[str, Any]] = []
    seen_pairs: Set[Tuple[str, str]] = set()

    for house_a, lord_a in sorted(house_lords.items()):
        if lord_a not in planets:
            continue

        sign_lord_a = get_planet_sign_lord(planets[lord_a])
        if not sign_lord_a:
            continue

        for house_b, lord_b in sorted(house_lords.items()):
            if house_a >= house_b or lord_a == lord_b:
                continue
            if lord_b not in planets:
                continue

            sign_lord_b = get_planet_sign_lord(planets[lord_b])

            if sign_lord_a != lord_b or sign_lord_b != lord_a:
                continue

            pair = tuple(sorted((lord_a, lord_b)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            house_of_lord_a = (
                normalize_house_mapping_value(planet_house_mapping[lord_a])
                if planet_house_mapping and lord_a in planet_house_mapping
                else None
            )
            house_of_lord_b = (
                normalize_house_mapping_value(planet_house_mapping[lord_b])
                if planet_house_mapping and lord_b in planet_house_mapping
                else None
            )

            exchanges.append({
                "type": "sign_exchange",
                "yoga_relationship": "parivartana",
                "planet_a": lord_a,
                "planet_b": lord_b,
                "house_a": house_a,
                "house_b": house_b,
                "house_a_group": house_group(house_a),
                "house_b_group": house_group(house_b),
                "planet_a_sign": get_planet_sign(planets[lord_a]),
                "planet_b_sign": get_planet_sign(planets[lord_b]),
                "planet_a_house": house_of_lord_a,
                "planet_b_house": house_of_lord_b,
            })

    return exchanges


# ---------------------------------------------------------------------------
# MASTER RELATIONSHIP ENGINE
# ---------------------------------------------------------------------------

def build_planet_relationships(
    planets: Dict[str, Dict[str, Any]],
    house_lords: Optional[Dict[int, str]] = None,
    planet_house_mapping: Optional[Dict[str, Any]] = None,
    lagna_sign: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the complete relationship data layer.

    Existing callers that only pass `planets` remain supported.
    """
    result: Dict[str, Any] = {
        "relationship_tradition": RELATIONSHIP_TRADITION,
        "planet_to_planet": build_planet_to_planet_relationships(planets),
        "planet_to_sign_lord": build_all_sign_lord_relationships(planets),
        "planet_to_house_lord": [],
        "planet_to_house": [],
        "house_lord_relationships": [],
        "functional_planet_relationships": [],
        "parivartana": [],
        "badhakesh": None,
        "dispositor_chains": {
            planet: get_dispositor_chain(planet, planets)
            for planet in PLANETS
            if planet in planets
        },
    }

    if house_lords:
        result["planet_to_house_lord"] = [
            {
                "house": house,
                "house_lord": lord,
                "house_group": house_group(house),
                "planet": planet,
                "natural_relationship": natural_relationship(planet, lord),
                "same_planet": planet == lord,
            }
            for house, lord in sorted(house_lords.items())
            for planet in PLANETS
            if planet in planets
        ]

        result["functional_planet_relationships"] = (
            build_functional_planet_relationships(house_lords)
        )

        result["house_lord_relationships"] = build_house_lord_relationships(
            planets,
            house_lords,
            planet_house_mapping,
        )

        result["parivartana"] = detect_parivartana_yogas(
            planets,
            house_lords,
            planet_house_mapping,
        )

        if lagna_sign:
            result["badhakesh"] = build_badhakesh_relationship(
                lagna_sign,
                house_lords,
            )

    if planet_house_mapping and house_lords:
        result["planet_to_house"] = build_planet_house_relationships(
            planets,
            planet_house_mapping,
            house_lords,
        )

    return result


# ---------------------------------------------------------------------------
# QUERY HELPERS FOR YOGA ENGINE
# ---------------------------------------------------------------------------

def get_conjunct_planets(
    planet_name: str,
    relationships: List[Dict[str, Any]],
) -> List[str]:
    """Return planets occupying the same sign as the requested planet."""
    result: List[str] = []

    for relationship in relationships:
        if not relationship.get("same_sign"):
            continue

        if relationship.get("planet_a") == planet_name:
            result.append(relationship["planet_b"])
        elif relationship.get("planet_b") == planet_name:
            result.append(relationship["planet_a"])

    return result


def get_planet_relationship(
    planet_a: str,
    planet_b: str,
    relationships: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Retrieve a specific planet-to-planet relationship."""
    for relationship in relationships:
        same_direction = (
            relationship.get("planet_a") == planet_a
            and relationship.get("planet_b") == planet_b
        )
        reverse_direction = (
            relationship.get("planet_a") == planet_b
            and relationship.get("planet_b") == planet_a
        )

        if same_direction or reverse_direction:
            return relationship

    return None


def planets_have_yuti(
    planet_a: str,
    planet_b: str,
    relationships: List[Dict[str, Any]],
) -> bool:
    """Return True when two planets share a sign in the relationship layer."""
    relationship = get_planet_relationship(planet_a, planet_b, relationships)
    return bool(relationship and relationship.get("yuti"))


def get_house_lord(
    house_number: int,
    house_lords: Dict[int, str],
) -> Optional[str]:
    """Convenience accessor for Yoga rules."""
    return house_lords.get(house_number)


def get_planet_house(
    planet_name: str,
    planet_house_mapping: Dict[str, Any],
) -> Optional[int]:
    """Return a planet's normalized house number."""
    return normalize_house_mapping_value(
        planet_house_mapping.get(planet_name)
    )


def get_owned_houses(
    planet_name: str,
    house_lords: Dict[int, str],
) -> List[int]:
    """Convenience accessor for a planet's owned houses."""
    return get_houses_owned_by_planet(planet_name, house_lords)


def has_parivartana(
    planet_a: str,
    planet_b: str,
    parivartana_records: List[Dict[str, Any]],
) -> bool:
    """Check whether two planets have a detected sign exchange."""
    target = {planet_a, planet_b}
    return any(
        {record.get("planet_a"), record.get("planet_b")} == target
        for record in parivartana_records
    )
