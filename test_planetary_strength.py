"""Independent tests for planetary_strength.py."""

import json

from planets import calculate_planets
from planetary_strength import calculate_dignity, calculate_strength


# ---------------------------------------------------------------
# Classical dignity unit tests
# ---------------------------------------------------------------

assert calculate_dignity("Sun", 0, 10)["dignity"] == "exalted"
assert calculate_dignity("Sun", 0, 10)["is_deep_exaltation"] is True

assert calculate_dignity("Sun", 4, 10)["dignity"] == "moolatrikona"
assert calculate_dignity("Sun", 4, 25)["dignity"] == "own_sign"

assert calculate_dignity("Sun", 6, 10)["dignity"] == "debilitated"
assert calculate_dignity("Sun", 6, 10)["is_deep_debilitation"] is True

assert calculate_dignity("Saturn", 6, 20)["dignity"] == "exalted"
assert calculate_dignity("Jupiter", 9, 5)["dignity"] == "debilitated"
assert calculate_dignity("Venus", 11, 27)["dignity"] == "exalted"
assert calculate_dignity("Mars", 9, 28)["dignity"] == "exalted"


# ---------------------------------------------------------------
# Compatibility test with the existing planets.py
# ---------------------------------------------------------------

# Fixed Julian Day. The exact date is irrelevant; this is only a
# deterministic compatibility test between planets.py and the new engine.
julian_day = 2451545.0

planets = calculate_planets(julian_day)
strengths = calculate_strength(planets)

expected_planets = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
]

for planet in expected_planets:
    assert planet in strengths, f"Missing strength result for {planet}"
    assert "sign" in strengths[planet]
    assert "sign_index" in strengths[planet]
    assert "degree_in_sign" in strengths[planet]
    assert "sign_lord" in strengths[planet]
    assert "dignity" in strengths[planet]
    assert "dignity_score" in strengths[planet]
    assert "retrograde" in strengths[planet]
    assert "combustion" in strengths[planet]


print("PLANETARY STRENGTH TEST: PASS")
print(json.dumps(strengths, indent=2))
