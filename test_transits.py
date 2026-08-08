from transits import calculate_transits


def test_transit_output():
    # Known Julian Day:
    # 2000-01-01 12:00 UT
    julian_day = 2451545.0

    result = calculate_transits(julian_day)

    required_planets = [
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

    # Check all planets exist
    for planet in required_planets:
        assert planet in result, f"Missing planet: {planet}"

    # Check required fields
    for planet in required_planets:
        data = result[planet]

        assert "longitude" in data
        assert "latitude" in data
        assert "sign" in data
        assert "sign_index" in data
        assert "degree_in_sign" in data
        assert "degree_dms" in data
        assert "speed" in data
        assert "retrograde" in data

        assert 0 <= data["longitude"] < 360
        assert 0 <= data["sign_index"] <= 11
        assert 0 <= data["degree_in_sign"] < 30

    # Rahu/Ketu must be exactly 180° apart
    rahu = result["Rahu"]["longitude"]
    ketu = result["Ketu"]["longitude"]

    separation = abs(rahu - ketu)

    if separation > 180:
        separation = 360 - separation

    assert abs(separation - 180) < 0.000001

    print("TRANSIT ENGINE TEST: PASS")


if __name__ == "__main__":
    test_transit_output()
