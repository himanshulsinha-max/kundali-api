
"""
Ashtakavarga Engine
-------------------

Classical Parashari/Raman-style Ashtakavarga calculation layer.

Scope:
- Seven Bhinnashtakavarga (BAV) tables:
  Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
- Eight contributors to each BAV:
  Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna
- Raw Sarvashtakavarga (SAV)
- 337-point checksum
- Per-planet checksum validation
- Whole-Sign house score mapping
- Transit score helpers
- Optional Trikona + Ekadhipatya reduction helpers

Rahu and Ketu are NOT contributors to Ashtakavarga.

The interpretation layer is intentionally kept separate from the
mathematical calculation layer.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Dict, List, Mapping, Optional


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

SIGN_INDEX = {sign: i for i, sign in enumerate(SIGNS)}

PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
]

CONTRIBUTORS = PLANETS + ["Lagna"]

EXPECTED_TOTALS = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}

# Benefic house positions for each BAV target planet, counted from
# each contributor. These are the fixed classical positions used
# by this engine.
BENEFIC_POSITIONS: Dict[str, Dict[str, List[int]]] = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

TRIKONA_GROUPS = [
    (0, 4, 8),   # Aries, Leo, Sagittarius
    (1, 5, 9),   # Taurus, Virgo, Capricorn
    (2, 6, 10),  # Gemini, Libra, Aquarius
    (3, 7, 11),  # Cancer, Scorpio, Pisces
]

DUAL_OWNERSHIP_PAIRS = [
    (0, 7),   # Mars: Aries, Scorpio
    (1, 6),   # Venus: Taurus, Libra
    (2, 5),   # Mercury: Gemini, Virgo
    (8, 11),  # Jupiter: Sagittarius, Pisces
    (9, 10),  # Saturn: Capricorn, Aquarius
]

ALIASES = {
    "surya": "Sun",
    "sun": "Sun",
    "chandra": "Moon",
    "moon": "Moon",
    "mangal": "Mars",
    "mars": "Mars",
    "budha": "Mercury",
    "mercury": "Mercury",
    "guru": "Jupiter",
    "jupiter": "Jupiter",
    "shukra": "Venus",
    "venus": "Venus",
    "shani": "Saturn",
    "saturn": "Saturn",
}


def _canonical_planet(name: str) -> str:
    key = str(name).strip().lower()
    if key in ALIASES:
        return ALIASES[key]
    return str(name).strip()


def _normalize_sign(sign: Any) -> str:
    if isinstance(sign, int):
        if 0 <= sign <= 11:
            return SIGNS[sign]
        if 1 <= sign <= 12:
            return SIGNS[sign - 1]

    if isinstance(sign, float) and sign.is_integer():
        return _normalize_sign(int(sign))

    if not isinstance(sign, str):
        raise ValueError(f"Invalid sign value: {sign!r}")

    cleaned = sign.strip().lower()
    for canonical in SIGNS:
        if canonical.lower() == cleaned:
            return canonical

    raise ValueError(f"Unknown zodiac sign: {sign!r}")


def _extract_sign(value: Any) -> str:
    if isinstance(value, Mapping):
        if value.get("sign") is not None:
            return _normalize_sign(value["sign"])
        if value.get("sign_index") is not None:
            return _normalize_sign(value["sign_index"])
        if value.get("rashi") is not None:
            return _normalize_sign(value["rashi"])
        if value.get("rashi_index") is not None:
            return _normalize_sign(value["rashi_index"])

    return _normalize_sign(value)


def _relative_house(reference_sign_index: int, target_sign_index: int) -> int:
    return ((target_sign_index - reference_sign_index) % 12) + 1


def _validate_planet_positions(
    planets: Mapping[str, Mapping[str, Any]],
    lagna_sign: Any,
) -> Dict[str, str]:
    if not isinstance(planets, Mapping):
        raise TypeError("planets must be a dictionary.")

    normalized: Dict[str, str] = {}

    for name, value in planets.items():
        canonical = _canonical_planet(name)
        if canonical in PLANETS:
            normalized[canonical] = _extract_sign(value)

    missing = [planet for planet in PLANETS if planet not in normalized]
    if missing:
        raise ValueError(
            "Ashtakavarga requires all seven classical planets. "
            f"Missing: {', '.join(missing)}"
        )

    normalized["Lagna"] = _extract_sign(lagna_sign)
    return normalized


def build_prastara_table(
    target_planet: str,
    positions: Mapping[str, str],
) -> Dict[str, Dict[str, int]]:
    """
    Return the 8 x 12 binary contributor matrix for one BAV.

    Rows = contributors.
    Columns = zodiac signs.
    Value 1 = benefic bindu, 0 = no bindu.
    """
    target_planet = _canonical_planet(target_planet)

    if target_planet not in PLANETS:
        raise ValueError(f"Invalid BAV target: {target_planet}")

    result: Dict[str, Dict[str, int]] = {}

    for contributor in CONTRIBUTORS:
        reference_sign = positions[contributor]
        reference_index = SIGN_INDEX[reference_sign]
        benefic_houses = set(
            BENEFIC_POSITIONS[target_planet][contributor]
        )

        row: Dict[str, int] = {}
        for sign in SIGNS:
            target_index = SIGN_INDEX[sign]
            house = _relative_house(reference_index, target_index)
            row[sign] = 1 if house in benefic_houses else 0

        result[contributor] = row

    return result


def build_bhinnashtakavarga(
    target_planet: str,
    positions: Mapping[str, str],
) -> Dict[str, Any]:
    """Calculate one complete raw BAV table."""
    target_planet = _canonical_planet(target_planet)
    prastara = build_prastara_table(target_planet, positions)

    bindus = {
        sign: sum(prastara[contributor][sign] for contributor in CONTRIBUTORS)
        for sign in SIGNS
    }

    total = sum(bindus.values())
    expected = EXPECTED_TOTALS[target_planet]

    if total != expected:
        raise AssertionError(
            f"{target_planet} BAV checksum failed: "
            f"got {total}, expected {expected}"
        )

    return {
        "planet": target_planet,
        "bindus": bindus,
        "total": total,
        "expected_total": expected,
        "checksum_passed": total == expected,
        "prastara": prastara,
    }


def build_sarvashtakavarga(
    bav_tables: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    """
    Build raw Sarvashtakavarga from the seven BAV tables.

    SAV uses the unreduced BAV tables.
    """
    bindus = {
        sign: sum(
            int(bav_tables[planet]["bindus"][sign])
            for planet in PLANETS
        )
        for sign in SIGNS
    }

    total = sum(bindus.values())

    if total != 337:
        raise AssertionError(
            f"SAV checksum failed: got {total}, expected 337"
        )

    return {
        "bindus": bindus,
        "total": total,
        "expected_total": 337,
        "checksum_passed": total == 337,
    }


def score_classification(score: int) -> str:
    """Neutral calculation-only classification; interpretation is separate."""
    if score <= 1:
        return "very_poor"
    if score <= 3:
        return "poor"
    if score == 4:
        return "neutral"
    if score <= 6:
        return "good"
    return "excellent"


def sav_classification(score: int) -> str:
    """
    Non-predictive SAV banding.

    The Masterfile explicitly states:
      - 28 bindus = average
      - <24 = weak
      - >30 = superior

    It does not define every intermediate score, so those values are
    labelled intermediate rather than inventing a stronger interpretation.
    """
    if score > 30:
        return "superior"
    if score == 28:
        return "average"
    if score < 24:
        return "weak"
    return "intermediate"


def build_house_scores(
    sav_bindus: Mapping[str, int],
    lagna_sign: str,
) -> Dict[int, Dict[str, Any]]:
    """Map raw SAV sign scores onto Whole-Sign houses."""
    lagna_index = SIGN_INDEX[lagna_sign]
    result: Dict[int, Dict[str, Any]] = {}

    for house in range(1, 13):
        sign = SIGNS[(lagna_index + house - 1) % 12]
        score = int(sav_bindus[sign])
        result[house] = {
            "house": house,
            "sign": sign,
            "bindus": score,
            "classification": sav_classification(score),
        }

    return result


def transit_score(
    bav_tables: Mapping[str, Mapping[str, Any]],
    transit_planet: str,
    transit_sign: Any,
) -> Dict[str, Any]:
    """Return the BAV score for a planet transiting a sign."""
    planet = _canonical_planet(transit_planet)
    if planet not in PLANETS:
        raise ValueError(f"Invalid transit planet: {transit_planet}")

    sign = _normalize_sign(transit_sign)
    score = int(bav_tables[planet]["bindus"][sign])

    return {
        "planet": planet,
        "transit_sign": sign,
        "bindus": score,
        "max_bindus": 8,
        "malefic_units": 8 - score,
        "classification": score_classification(score),
    }


def _trikona_reduction(values: List[int]) -> List[int]:
    """
    Apply the standard Trikona reduction to one 3-sign triangle.

    Rules:
    - if all are equal, all become zero;
    - if one is zero, leave the others unchanged;
    - otherwise subtract the minimum from all three.
    """
    a, b, c = values

    if a == b == c:
        return [0, 0, 0]

    if 0 in values:
        return values[:]

    minimum = min(values)
    return [a - minimum, b - minimum, c - minimum]


def apply_trikona_reduction(
    bindus: Mapping[str, int],
) -> Dict[str, int]:
    """Return a copy of a BAV table after Trikona reduction."""
    reduced = {sign: int(bindus[sign]) for sign in SIGNS}

    for indexes in TRIKONA_GROUPS:
        values = [reduced[SIGNS[i]] for i in indexes]
        new_values = _trikona_reduction(values)

        for index, value in zip(indexes, new_values):
            reduced[SIGNS[index]] = value

    return reduced


def apply_ekadhipatya_reduction(
    bindus: Mapping[str, int],
    occupied_signs: Optional[List[str]] = None,
) -> Dict[str, int]:
    """
    Apply Ekadhipatya reduction to a BAV.

    occupied_signs should contain signs occupied by planets.
    Cancer and Leo are excluded because they have single ownership.
    """
    reduced = {sign: int(bindus[sign]) for sign in SIGNS}
    occupied = {
        _normalize_sign(sign)
        for sign in (occupied_signs or [])
    }

    for first_index, second_index in DUAL_OWNERSHIP_PAIRS:
        first_sign = SIGNS[first_index]
        second_sign = SIGNS[second_index]

        a = reduced[first_sign]
        b = reduced[second_sign]

        if a == 0 or b == 0:
            continue

        a_occupied = first_sign in occupied
        b_occupied = second_sign in occupied

        if a_occupied and b_occupied:
            continue

        if a_occupied and not b_occupied:
            if a < b:
                reduced[second_sign] = a
            else:
                reduced[second_sign] = 0
            continue

        if b_occupied and not a_occupied:
            if b < a:
                reduced[first_sign] = b
            else:
                reduced[first_sign] = 0
            continue

        # Neither occupied.
        if a == b:
            reduced[first_sign] = 0
            reduced[second_sign] = 0
        elif a < b:
            reduced[second_sign] = a
        else:
            reduced[first_sign] = b

    return reduced


def build_reduced_bav(
    bav_table: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    """
    Apply Trikona + Ekadhipatya reduction to one BAV.

    These reductions are kept separate from raw BAV/SAV because
    raw BAV is the primary transit/SAV data layer.
    """
    raw = {
        sign: int(bav_table["bindus"][sign])
        for sign in SIGNS
    }

    trine_reduced = apply_trikona_reduction(raw)

    occupied_signs = []
    for name, value in planets.items():
        canonical = _canonical_planet(name)
        if canonical in PLANETS:
            occupied_signs.append(_extract_sign(value))

    final = apply_ekadhipatya_reduction(
        trine_reduced,
        occupied_signs=occupied_signs,
    )

    return {
        "planet": bav_table["planet"],
        "before_reduction": raw,
        "after_trikona_reduction": trine_reduced,
        "after_ekadhipatya_reduction": final,
        "total_before_reduction": sum(raw.values()),
        "total_after_reduction": sum(final.values()),
    }


def build_ashtakavarga(
    planets: Mapping[str, Mapping[str, Any]],
    lagna_sign: Any,
) -> Dict[str, Any]:
    """
    Master Ashtakavarga calculation.

    Returns:
      - normalized positions
      - all seven BAV tables
      - raw SAV
      - Whole-Sign house scores
      - validation checks
      - transit helper metadata
      - reduced BAV tables for downstream longevity work
    """
    positions = _validate_planet_positions(planets, lagna_sign)

    bav_tables: Dict[str, Any] = {}

    for planet in PLANETS:
        bav_tables[planet] = build_bhinnashtakavarga(
            planet,
            positions,
        )

    sav = build_sarvashtakavarga(bav_tables)

    house_scores = build_house_scores(
        sav["bindus"],
        positions["Lagna"],
    )

    reduced_bav = {
        planet: build_reduced_bav(
            bav_tables[planet],
            planets,
        )
        for planet in PLANETS
    }

    return {
        "engine": "ashtakavarga",
        "version": "1.0",
        "system": "parashari_raw_bav_sav",
        "house_system": "whole_sign",
        "contributors": CONTRIBUTORS,
        "nodes_included": False,
        "positions": positions,
        "bhinnashtakavarga": bav_tables,
        "sarvashtakavarga": sav,
        "house_scores": house_scores,
        "reduced_bhinnashtakavarga": reduced_bav,
        "validation": {
            "planet_totals": {
                planet: bav_tables[planet]["total"]
                for planet in PLANETS
            },
            "expected_planet_totals": EXPECTED_TOTALS,
            "planet_checks_passed": all(
                bav_tables[planet]["checksum_passed"]
                for planet in PLANETS
            ),
            "sarvashtakavarga_total": sav["total"],
            "sarvashtakavarga_expected": 337,
            "sarvashtakavarga_checksum_passed": sav["checksum_passed"],
            "grand_checksum_passed": (
                all(
                    bav_tables[planet]["checksum_passed"]
                    for planet in PLANETS
                )
                and sav["checksum_passed"]
            ),
        },
    }


def get_transit_score(
    ashtakavarga_data: Mapping[str, Any],
    transit_planet: str,
    transit_sign: Any,
) -> Dict[str, Any]:
    """Convenience wrapper for already-computed Ashtakavarga data."""
    return transit_score(
        ashtakavarga_data["bhinnashtakavarga"],
        transit_planet,
        transit_sign,
    )


if __name__ == "__main__":
    # Deterministic self-test.
    sample_planets = {
        "Sun": {"sign": "Cancer"},
        "Moon": {"sign": "Taurus"},
        "Mars": {"sign": "Leo"},
        "Mercury": {"sign": "Leo"},
        "Jupiter": {"sign": "Scorpio"},
        "Venus": {"sign": "Leo"},
        "Saturn": {"sign": "Taurus"},
        "Rahu": {"sign": "Gemini"},
        "Ketu": {"sign": "Sagittarius"},
    }

    result = build_ashtakavarga(
        sample_planets,
        lagna_sign="Aries",
    )

    assert result["validation"]["grand_checksum_passed"] is True
    assert result["sarvashtakavarga"]["total"] == 337
    assert result["bhinnashtakavarga"]["Sun"]["total"] == 48
    assert result["bhinnashtakavarga"]["Moon"]["total"] == 49
    assert result["bhinnashtakavarga"]["Mars"]["total"] == 39
    assert result["bhinnashtakavarga"]["Mercury"]["total"] == 54
    assert result["bhinnashtakavarga"]["Jupiter"]["total"] == 56
    assert result["bhinnashtakavarga"]["Venus"]["total"] == 52
    assert result["bhinnashtakavarga"]["Saturn"]["total"] == 39

    print(
        json.dumps(
            {
                "status": "OK",
                "grand_checksum": result["validation"]["grand_checksum_passed"],
                "planet_totals": result["validation"]["planet_totals"],
                "sav_total": result["sarvashtakavarga"]["total"],
            },
            indent=2,
        )
    )
