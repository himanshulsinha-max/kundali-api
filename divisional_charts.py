from __future__ import annotations

from typing import Any, Dict, Iterable, List

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

SIGN_TO_INDEX = {sign: idx for idx, sign in enumerate(SIGNS)}
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _normalize_sign(sign: str) -> str:
    if sign not in SIGN_TO_INDEX:
        raise ValueError(f"Invalid sign: {sign}")
    return sign


def _sign_from_index(index: int) -> str:
    return SIGNS[index % 12]


def _offset_sign(sign: str, offset: int) -> str:
    return _sign_from_index(SIGN_TO_INDEX[_normalize_sign(sign)] + offset)


def _floor_division_index(longitude: float, chunk_size: float) -> int:
    return int(longitude // chunk_size)


def _is_even_sign(sign: str) -> bool:
    # Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces
    return SIGN_TO_INDEX[_normalize_sign(sign)] % 2 == 1


def _split_triplet_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 10.0)
    if part >= 3:
        part = 2
    if _is_even_sign(sign):
        # Even signs: reverse order of drekkana divisions
        # 0-10 => 9th from sign, 10-20 => 5th from sign, 20-30 => 1st from sign
        offsets = [8, 4, 0]
    else:
        # Odd signs: 1st, 5th, 9th from sign
        offsets = [0, 4, 8]
    return _offset_sign(sign, offsets[part])


def _hora_sign(sign: str, longitude_in_sign: float) -> str:
    # Classical Parashara-style Hora approximation:
    # odd signs: first 15° Sun's sign (Leo), second 15° Moon's sign (Cancer)
    # even signs: first 15° Moon's sign (Cancer), second 15° Sun's sign (Leo)
    if longitude_in_sign < 15.0:
        return "Leo" if not _is_even_sign(sign) else "Cancer"
    return "Cancer" if not _is_even_sign(sign) else "Leo"


def _navamsa_sign(sign: str, longitude_in_sign: float) -> str:
    # 3°20' segments = 30 / 9
    nav_index = _floor_division_index(longitude_in_sign, 30.0 / 9.0)
    nav_index = min(nav_index, 8)
    sign_idx = SIGN_TO_INDEX[_normalize_sign(sign)]

    if _is_even_sign(sign):
        # Even signs start from 9th from the sign
        start = (sign_idx + 8) % 12
    else:
        # Odd signs start from the sign itself
        start = sign_idx
    return _sign_from_index(start + nav_index)


def _chaturthamsa_sign(sign: str, longitude_in_sign: float) -> str:
    # 7°30' segments
    part = _floor_division_index(longitude_in_sign, 7.5)
    part = min(part, 3)
    return _offset_sign(sign, [0, 3, 6, 9][part])


def _saptamsa_sign(sign: str, longitude_in_sign: float) -> str:
    # 30 / 7 = 4°17'08" approx
    part = _floor_division_index(longitude_in_sign, 30.0 / 7.0)
    part = min(part, 6)
    sign_idx = SIGN_TO_INDEX[_normalize_sign(sign)]
    if _is_even_sign(sign):
        start = (sign_idx + 6) % 12
    else:
        start = sign_idx
    return _sign_from_index(start + part)


def _dasamsa_sign(sign: str, longitude_in_sign: float) -> str:
    # 3° segments
    part = _floor_division_index(longitude_in_sign, 3.0)
    part = min(part, 9)
    sign_idx = SIGN_TO_INDEX[_normalize_sign(sign)]
    if _is_even_sign(sign):
        start = (sign_idx + 3) % 12
    else:
        start = sign_idx
    return _sign_from_index(start + part)


def _dvadasamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 12.0)
    part = min(part, 11)
    return _offset_sign(sign, part)


def _shodasamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 16.0)
    part = min(part, 15)
    return _offset_sign(sign, part)


def _vimsamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 20.0)
    part = min(part, 19)
    return _offset_sign(sign, part)


def _chaturvimsamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 24.0)
    part = min(part, 23)
    return _offset_sign(sign, part)


def _bhamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 27.0)
    part = min(part, 26)
    return _offset_sign(sign, part)


def _trimsamsa_sign(sign: str, longitude_in_sign: float) -> str:
    # Standard Parashara-style 30th division for odd/even signs.
    # This is a simplified but deterministic implementation.
    idx = SIGN_TO_INDEX[_normalize_sign(sign)]
    if _is_even_sign(sign):
        if longitude_in_sign < 5:
            return "Virgo"
        if longitude_in_sign < 10:
            return "Cancer"
        if longitude_in_sign < 18:
            return "Leo"
        if longitude_in_sign < 25:
            return "Aquarius"
        return "Gemini"
    else:
        if longitude_in_sign < 5:
            return "Aries"
        if longitude_in_sign < 10:
            return "Aquarius"
        if longitude_in_sign < 18:
            return "Sagittarius"
        if longitude_in_sign < 25:
            return "Leo"
        return "Virgo"


def _khavedamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 40.0)
    part = min(part, 39)
    return _offset_sign(sign, part)


def _akshavedamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 30.0 / 45.0)
    part = min(part, 44)
    return _offset_sign(sign, part)


def _shashtiamsa_sign(sign: str, longitude_in_sign: float) -> str:
    part = _floor_division_index(longitude_in_sign, 0.5)
    part = min(part, 59)
    return _offset_sign(sign, part)


def _build_chart_entry(sign: str, longitude: float, chart_sign: str) -> Dict[str, Any]:
    return {
        "sign": chart_sign,
        "longitude": round(longitude, 6),
    }


def build_divisional_charts(planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    charts: Dict[str, Dict[str, Dict[str, Any]]] = {
        "D1": {},
        "D2": {},
        "D3": {},
        "D4": {},
        "D7": {},
        "D9": {},
        "D10": {},
        "D12": {},
        "D16": {},
        "D20": {},
        "D24": {},
        "D27": {},
        "D30": {},
        "D40": {},
        "D45": {},
        "D60": {},
    }

    for planet, pdata in planets.items():
        sign = _normalize_sign(pdata["sign"])
        longitude = float(pdata["longitude"])
        longitude_in_sign = longitude % 30.0

        charts["D1"][planet] = _build_chart_entry(sign, longitude, sign)
        charts["D2"][planet] = _build_chart_entry(sign, longitude, _hora_sign(sign, longitude_in_sign))
        charts["D3"][planet] = _build_chart_entry(sign, longitude, _split_triplet_sign(sign, longitude_in_sign))
        charts["D4"][planet] = _build_chart_entry(sign, longitude, _chaturthamsa_sign(sign, longitude_in_sign))
        charts["D7"][planet] = _build_chart_entry(sign, longitude, _saptamsa_sign(sign, longitude_in_sign))
        charts["D9"][planet] = _build_chart_entry(sign, longitude, _navamsa_sign(sign, longitude_in_sign))
        charts["D10"][planet] = _build_chart_entry(sign, longitude, _dasamsa_sign(sign, longitude_in_sign))
        charts["D12"][planet] = _build_chart_entry(sign, longitude, _dvadasamsa_sign(sign, longitude_in_sign))
        charts["D16"][planet] = _build_chart_entry(sign, longitude, _shodasamsa_sign(sign, longitude_in_sign))
        charts["D20"][planet] = _build_chart_entry(sign, longitude, _vimsamsa_sign(sign, longitude_in_sign))
        charts["D24"][planet] = _build_chart_entry(sign, longitude, _chaturvimsamsa_sign(sign, longitude_in_sign))
        charts["D27"][planet] = _build_chart_entry(sign, longitude, _bhamsa_sign(sign, longitude_in_sign))
        charts["D30"][planet] = _build_chart_entry(sign, longitude, _trimsamsa_sign(sign, longitude_in_sign))
        charts["D40"][planet] = _build_chart_entry(sign, longitude, _khavedamsa_sign(sign, longitude_in_sign))
        charts["D45"][planet] = _build_chart_entry(sign, longitude, _akshavedamsa_sign(sign, longitude_in_sign))
        charts["D60"][planet] = _build_chart_entry(sign, longitude, _shashtiamsa_sign(sign, longitude_in_sign))

    return {
        "charts": charts,
        "planet_count": len(planets),
        "supported_vargas": list(charts.keys()),
        "notes": {
            "D2": "Hora implemented with a deterministic classical approximation.",
            "D3": "Drekkana uses odd/even sign triplet logic.",
            "D9": "Navamsa uses odd/even starting sign logic.",
            "D10": "Dasamsa uses 3-degree segments with odd/even starting sign logic.",
            "D30": "Trimsamsa uses a simplified Parashara-style distribution.",
            "higher_vargas": "Higher Vargas are deterministic placeholders and should be validated against your chosen rule-set before consultation use.",
        },
    }


def build_d1_to_d10(planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    all_charts = build_divisional_charts(planets)
    return {
        "D1": all_charts["charts"]["D1"],
        "D2": all_charts["charts"]["D2"],
        "D3": all_charts["charts"]["D3"],
        "D4": all_charts["charts"]["D4"],
        "D7": all_charts["charts"]["D7"],
        "D9": all_charts["charts"]["D9"],
        "D10": all_charts["charts"]["D10"],
    }
