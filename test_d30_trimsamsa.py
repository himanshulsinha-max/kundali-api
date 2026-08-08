"""Independent tests for the Parashari D30 Trimsamsa engine."""

from d30_trimsamsa import (
    get_d30_sign,
    get_trimsamsa_lord,
    build_d30,
)


# Odd-sign sequence
assert get_trimsamsa_lord("Aries", 0.0) == "Mars"
assert get_trimsamsa_lord("Aries", 5.0) == "Saturn"
assert get_trimsamsa_lord("Aries", 10.0) == "Jupiter"
assert get_trimsamsa_lord("Aries", 18.0) == "Mercury"
assert get_trimsamsa_lord("Aries", 25.0) == "Venus"
assert get_d30_sign("Aries", 2.0) == "Aries"
assert get_d30_sign("Aries", 7.0) == "Aquarius"
assert get_d30_sign("Aries", 12.0) == "Sagittarius"
assert get_d30_sign("Aries", 20.0) == "Gemini"
assert get_d30_sign("Aries", 27.0) == "Libra"

# Even-sign reverse sequence
assert get_trimsamsa_lord("Taurus", 0.0) == "Venus"
assert get_trimsamsa_lord("Taurus", 5.0) == "Mercury"
assert get_trimsamsa_lord("Taurus", 12.0) == "Jupiter"
assert get_trimsamsa_lord("Taurus", 20.0) == "Saturn"
assert get_trimsamsa_lord("Taurus", 25.0) == "Mars"
assert get_d30_sign("Taurus", 2.0) == "Taurus"
assert get_d30_sign("Taurus", 8.0) == "Virgo"
assert get_d30_sign("Taurus", 15.0) == "Pisces"
assert get_d30_sign("Taurus", 22.0) == "Capricorn"
assert get_d30_sign("Taurus", 27.0) == "Scorpio"

# Integration shape test
planets = {
    "Sun": {"sign": "Leo", "degree_in_sign": 15.0},
    "Moon": {"sign": "Taurus", "degree_in_sign": 14.0},
    "Mars": {"sign": "Capricorn", "degree_in_sign": 28.0},
}

result = build_d30(planets)

assert set(result) == {"Sun", "Moon", "Mars"}
assert result["Sun"]["trimsamsa_lord"] == "Jupiter"
assert result["Moon"]["trimsamsa_lord"] == "Jupiter"
assert result["Mars"]["trimsamsa_lord"] == "Mars"

print("D30 TRIMSAMSA TEST: PASS")
