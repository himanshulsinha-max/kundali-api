from ashtakavarga import (
    PLANETS,
    SIGNS,
    build_ashtakavarga,
    build_bhinnashtakavarga,
    build_prastara_table,
    build_sarvashtakavarga,
)


SAMPLE_PLANETS = {
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


EXPECTED_BAV_TOTALS = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}

EXPECTED_SAMPLE_SAV = {
    "Aries": 29,
    "Taurus": 31,
    "Gemini": 36,
    "Cancer": 27,
    "Leo": 24,
    "Virgo": 31,
    "Libra": 27,
    "Scorpio": 20,
    "Sagittarius": 25,
    "Capricorn": 30,
    "Aquarius": 28,
    "Pisces": 29,
}


def test_every_bav_has_classical_checksum():
    positions = {
        "Sun": "Cancer",
        "Moon": "Taurus",
        "Mars": "Leo",
        "Mercury": "Leo",
        "Jupiter": "Scorpio",
        "Venus": "Leo",
        "Saturn": "Taurus",
        "Lagna": "Aries",
    }

    for planet in PLANETS:
        result = build_bhinnashtakavarga(planet, positions)
        assert result["total"] == EXPECTED_BAV_TOTALS[planet]
        assert result["checksum_passed"] is True
        assert set(result["bindus"]) == set(SIGNS)


def test_sample_sarvashtakavarga_matches_fixed_reference():
    result = build_ashtakavarga(SAMPLE_PLANETS, "Aries")

    assert result["validation"]["grand_checksum_passed"] is True
    assert result["sarvashtakavarga"]["total"] == 337
    assert result["sarvashtakavarga"]["bindus"] == EXPECTED_SAMPLE_SAV


def test_prastara_is_eight_by_twelve_and_binary():
    positions = {
        "Sun": "Aries",
        "Moon": "Aries",
        "Mars": "Aries",
        "Mercury": "Aries",
        "Jupiter": "Aries",
        "Venus": "Aries",
        "Saturn": "Aries",
        "Lagna": "Aries",
    }

    table = build_prastara_table("Sun", positions)

    assert set(table) == {
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
        "Lagna",
    }
    assert all(set(row) == set(SIGNS) for row in table.values())
    assert all(value in (0, 1) for row in table.values() for value in row.values())


def test_nodes_do_not_contribute_to_ashtakavarga():
    base = build_ashtakavarga(SAMPLE_PLANETS, "Aries")

    with_nodes_removed = dict(SAMPLE_PLANETS)
    with_nodes_removed.pop("Rahu")
    with_nodes_removed.pop("Ketu")
    without_nodes = build_ashtakavarga(with_nodes_removed, "Aries")

    assert base["sarvashtakavarga"] == without_nodes["sarvashtakavarga"]
    assert base["bhinnashtakavarga"] == without_nodes["bhinnashtakavarga"]


def test_sarvashtakavarga_rejects_bad_total():
    positions = {
        "Sun": "Cancer",
        "Moon": "Taurus",
        "Mars": "Leo",
        "Mercury": "Leo",
        "Jupiter": "Scorpio",
        "Venus": "Leo",
        "Saturn": "Taurus",
        "Lagna": "Aries",
    }

    bav = {
        planet: build_bhinnashtakavarga(planet, positions)
        for planet in PLANETS
    }
    bav["Sun"]["bindus"]["Aries"] += 1

    try:
        build_sarvashtakavarga(bav)
    except AssertionError as exc:
        assert "SAV checksum failed" in str(exc)
    else:
        raise AssertionError("Invalid SAV checksum was not rejected")
