from divisional_charts import build_divisional_charts


def test_divisional_chart_structure():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 10.0,
        },
        "Moon": {
            "sign": "Taurus",
            "longitude": 45.0,
        },
        "Mars": {
            "sign": "Gemini",
            "longitude": 75.0,
        },
    }

    result = build_divisional_charts(planets)

    assert "charts" in result

    expected_charts = [
        "D1",
        "D2",
        "D3",
        "D4",
        "D7",
        "D9",
        "D10",
        "D12",
    ]

    for chart in expected_charts:
        assert chart in result["charts"]


def test_d1_preserves_natal_sign():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 10.0,
        }
    }

    result = build_divisional_charts(planets)

    assert result["charts"]["D1"]["Sun"]["divisional_sign"] == "Aries"


def test_d2_odd_sign():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 10.0,
        }
    }

    result = build_divisional_charts(planets)

    # Aries is an odd sign.
    # First 15 degrees of an odd sign belong to Leo in D2.
    assert result["charts"]["D2"]["Sun"]["divisional_sign"] == "Leo"


def test_d2_even_sign():

    planets = {
        "Moon": {
            "sign": "Taurus",
            "longitude": 40.0,
        }
    }

    result = build_divisional_charts(planets)

    # Taurus is an even sign.
    # 40° = 10° within Taurus.
    # First 15 degrees of an even sign belong to Cancer.
    assert result["charts"]["D2"]["Moon"]["divisional_sign"] == "Cancer"


def test_d9_aries():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 0.0,
        }
    }

    result = build_divisional_charts(planets)

    # Aries is movable.
    # First Navamsa starts from Aries.
    assert result["charts"]["D9"]["Sun"]["divisional_sign"] == "Aries"


def test_d9_taurus():

    planets = {
        "Sun": {
            "sign": "Taurus",
            "longitude": 30.0,
        }
    }

    result = build_divisional_charts(planets)

    # Taurus is fixed.
    # First Navamsa starts from the 9th sign from Taurus = Capricorn.
    assert result["charts"]["D9"]["Sun"]["divisional_sign"] == "Capricorn"


def test_d10_aries():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 0.0,
        }
    }

    result = build_divisional_charts(planets)

    assert result["charts"]["D10"]["Sun"]["divisional_sign"] == "Aries"


def test_d12_first_division():

    planets = {
        "Sun": {
            "sign": "Aries",
            "longitude": 0.0,
        }
    }

    result = build_divisional_charts(planets)

    assert result["charts"]["D12"]["Sun"]["divisional_sign"] == "Aries"
