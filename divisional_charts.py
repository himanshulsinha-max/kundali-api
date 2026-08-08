from __future__ import annotations

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

SIGN_TO_INDEX = {sign: index for index, sign in enumerate(SIGNS)}


def _normalize_sign(sign: str) -> str:
    if sign not in SIGN_TO_INDEX:
        raise ValueError(f"Invalid sign: {sign}")
    return sign


def _sign_from_index(index: int) -> str:
    return SIGNS[index % 12]


def _offset_sign(sign: str, offset: int) -> str:
    return _sign_from_index(
        SIGN_TO_INDEX[_normalize_sign(sign)] + offset
    )


def _division_index(
    longitude_in_sign: float,
    divisions: int,
) -> int:
    """
    Return zero-based division index inside a 30° sign.

    Example:
        D9 = 9 divisions
        each division = 3°20'
    """
    if not 0.0 <= longitude_in_sign < 30.0:
        longitude_in_sign %= 30.0

    size = 30.0 / divisions
    index = int(longitude_in_sign // size)

    return min(index, divisions - 1)


def _sign_modality(sign: str) -> str:
    """
    Aries, Cancer, Libra, Capricorn = movable
    Taurus, Leo, Scorpio, Aquarius = fixed
    Gemini, Virgo, Sagittarius, Pisces = dual
    """
    index = SIGN_TO_INDEX[_normalize_sign(sign)]

    if index in (0, 3, 6, 9):
        return "movable"

    if index in (1, 4, 7, 10):
        return "fixed"

    return "dual"


def _is_odd_sign(sign: str) -> bool:
    return SIGN_TO_INDEX[_normalize_sign(sign)] % 2 == 0


def _hora_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D2 Hora.

    Odd signs:
        first 15°  -> Leo
        second 15° -> Cancer

    Even signs:
        first 15°  -> Cancer
        second 15° -> Leo
    """
    if _is_odd_sign(sign):
        return "Leo" if longitude_in_sign < 15.0 else "Cancer"

    return "Cancer" if longitude_in_sign < 15.0 else "Leo"


def _drekkana_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D3 Parashari Drekkana.

    1st division -> sign itself
    2nd division -> 5th from sign
    3rd division -> 9th from sign

    This sequence applies to both odd and even signs.
    """
    part = _division_index(longitude_in_sign, 3)

    offsets = [0, 4, 8]

    return _offset_sign(sign, offsets[part])


def _chaturthamsa_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D4 Chaturthamsa.

    The four divisions are 7°30' each.

    Movable signs:
        start from the sign itself.

    Fixed signs:
        start from the 4th sign.

    Dual signs:
        start from the 7th sign.
    """
    part = _division_index(longitude_in_sign, 4)

    modality = _sign_modality(sign)

    if modality == "movable":
        start_offset = 0
    elif modality == "fixed":
        start_offset = 3
    else:
        start_offset = 6

    return _offset_sign(
        sign,
        start_offset + part,
    )


def _saptamsa_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D7 Saptamsa.

    Odd signs:
        start from the sign itself.

    Even signs:
        start from the 7th sign.

    Each division = 30° / 7.
    """
    part = _division_index(longitude_in_sign, 7)

    if _is_odd_sign(sign):
        start_offset = 0
    else:
        start_offset = 6

    return _offset_sign(
        sign,
        start_offset + part,
    )


def _navamsa_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D9 Navamsa.

    Movable signs:
        start from the sign itself.

    Fixed signs:
        start from the 9th sign.

    Dual signs:
        start from the 5th sign.

    Each Navamsa = 3°20'.
    """
    part = _division_index(longitude_in_sign, 9)

    modality = _sign_modality(sign)

    if modality == "movable":
        start_offset = 0
    elif modality == "fixed":
        start_offset = 8
    else:
        start_offset = 4

    return _offset_sign(
        sign,
        start_offset + part,
    )


def _dasamsa_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D10 Dasamsa.

    Odd signs:
        start from the sign itself.

    Even signs:
        start from the 9th sign.

    Each division = 3°.
    """
    part = _division_index(longitude_in_sign, 10)

    if _is_odd_sign(sign):
        start_offset = 0
    else:
        start_offset = 8

    return _offset_sign(
        sign,
        start_offset + part,
    )


def _dvadasamsa_sign(
    sign: str,
    longitude_in_sign: float,
) -> str:
    """
    D12 Dvadasamsa.

    Each division = 2°30'.

    The first division starts from the natal sign,
    then proceeds sequentially through the zodiac.
    """
    part = _division_index(longitude_in_sign, 12)

    return _offset_sign(
        sign,
        part,
    )


def _build_entry(
    natal_sign: str,
    longitude: float,
    divisional_sign: str,
) -> Dict[str, Any]:
    return {
        "natal_sign": natal_sign,
        "longitude": round(longitude, 6),
        "divisional_sign": divisional_sign,
    }


def build_divisional_charts(
    planets: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:

    charts = {
        "D1": {},
        "D2": {},
        "D3": {},
        "D4": {},
        "D7": {},
        "D9": {},
        "D10": {},
        "D12": {},
    }

    for planet, data in planets.items():

        natal_sign = _normalize_sign(data["sign"])
        longitude = float(data["longitude"])

        longitude_in_sign = longitude % 30.0

        charts["D1"][planet] = _build_entry(
            natal_sign,
            longitude,
            natal_sign,
        )

        charts["D2"][planet] = _build_entry(
            natal_sign,
            longitude,
            _hora_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D3"][planet] = _build_entry(
            natal_sign,
            longitude,
            _drekkana_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D4"][planet] = _build_entry(
            natal_sign,
            longitude,
            _chaturthamsa_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D7"][planet] = _build_entry(
            natal_sign,
            longitude,
            _saptamsa_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D9"][planet] = _build_entry(
            natal_sign,
            longitude,
            _navamsa_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D10"][planet] = _build_entry(
            natal_sign,
            longitude,
            _dasamsa_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

        charts["D12"][planet] = _build_entry(
            natal_sign,
            longitude,
            _dvadasamsa_sign(
                natal_sign,
                longitude_in_sign,
            ),
        )

    return {
        "charts": charts,
        "supported_vargas": [
            "D1",
            "D2",
            "D3",
            "D4",
            "D7",
            "D9",
            "D10",
            "D12",
        ],
    }
