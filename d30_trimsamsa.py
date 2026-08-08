"""
D30 Trimsamsa Engine
--------------------

Parashari Trimsamsa (D30) calculation used as a dependency for
classical Saptavargaja Bala / Shadbala.

D30 uses unequal divisions of each 30-degree sign:

Odd signs:
    0-5   Mars
    5-10  Saturn
    10-18 Jupiter
    18-25 Mercury
    25-30 Venus

Even signs:
    0-5   Venus
    5-12  Mercury
    12-20 Jupiter
    20-25 Saturn
    25-30 Mars

The five Trimsamsa lords each correspond to their appropriate odd/even
sign for the actual D30 placement.
"""

from typing import Any, Dict


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
    "Pisces",
]

SIGN_INDEX = {sign: index for index, sign in enumerate(SIGNS)}


# Lord -> odd-sign / even-sign placement in D30.
TRIMSAMSA_SIGNS = {
    "Mars": ("Aries", "Scorpio"),
    "Saturn": ("Aquarius", "Capricorn"),
    "Jupiter": ("Sagittarius", "Pisces"),
    "Mercury": ("Gemini", "Virgo"),
    "Venus": ("Libra", "Taurus"),
}


ODD_DIVISIONS = (
    (0.0, 5.0, "Mars"),
    (5.0, 10.0, "Saturn"),
    (10.0, 18.0, "Jupiter"),
    (18.0, 25.0, "Mercury"),
    (25.0, 30.0, "Venus"),
)

EVEN_DIVISIONS = (
    (0.0, 5.0, "Venus"),
    (5.0, 12.0, "Mercury"),
    (12.0, 20.0, "Jupiter"),
    (20.0, 25.0, "Saturn"),
    (25.0, 30.0, "Mars"),
)


def normalize_sign(sign: str) -> str:
    if not isinstance(sign, str):
        raise TypeError("Sign must be a string.")

    sign = sign.strip().title()

    if sign not in SIGN_INDEX:
        raise ValueError(f"Invalid zodiac sign: {sign}")

    return sign


def normalize_degree(degree: float) -> float:
    degree = float(degree)

    if not 0.0 <= degree < 30.0:
        raise ValueError("degree_in_sign must be in the range 0 <= degree < 30.")

    return degree


def is_odd_sign(sign: str) -> bool:
    return SIGN_INDEX[normalize_sign(sign)] % 2 == 0


def get_trimsamsa_lord(sign: str, degree_in_sign: float) -> str:
    """Return the five-planet Trimsamsa lord for a natal sign/degree."""
    sign = normalize_sign(sign)
    degree = normalize_degree(degree_in_sign)

    divisions = ODD_DIVISIONS if is_odd_sign(sign) else EVEN_DIVISIONS

    for start, end, lord in divisions:
        if start <= degree < end:
            return lord

    # Degree is guaranteed to be < 30, so this is defensive only.
    raise RuntimeError("Unable to determine Trimsamsa lord.")


def get_d30_sign(sign: str, degree_in_sign: float) -> str:
    """Return the actual Parashari D30 sign placement."""
    sign = normalize_sign(sign)
    lord = get_trimsamsa_lord(sign, degree_in_sign)

    odd_sign, even_sign = TRIMSAMSA_SIGNS[lord]

    return odd_sign if is_odd_sign(sign) else even_sign


def calculate_d30_entry(
    planet: str,
    sign: str,
    degree_in_sign: float,
) -> Dict[str, Any]:
    """Calculate one planet's D30 placement."""
    sign = normalize_sign(sign)
    degree = normalize_degree(degree_in_sign)
    lord = get_trimsamsa_lord(sign, degree)
    d30_sign = get_d30_sign(sign, degree)

    return {
        "planet": planet,
        "natal_sign": sign,
        "degree_in_sign": round(degree, 8),
        "trimsamsa_lord": lord,
        "d30_sign": d30_sign,
    }


def build_d30(planets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build D30 placements for all supplied planetary data."""
    result = {}

    for planet, data in planets.items():
        if not isinstance(data, dict):
            raise TypeError(f"Invalid data for planet: {planet}")

        sign = data.get("sign")
        degree = data.get("degree_in_sign")

        if sign is None or degree is None:
            raise ValueError(
                f"Missing sign or degree_in_sign for {planet}"
            )

        result[planet] = calculate_d30_entry(
            planet,
            sign,
            degree,
        )

    return result
