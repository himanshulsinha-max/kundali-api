from d1_whole_sign import (
    house_from_sign,
    build_whole_sign_houses,
    build_d1_whole_sign,
)


def test_house_mapping():

    assert house_from_sign("Aries", "Aries") == 1
    assert house_from_sign("Aries", "Taurus") == 2
    assert house_from_sign("Aries", "Cancer") == 4
    assert house_from_sign("Aries", "Pisces") == 12

    assert house_from_sign("Cancer", "Cancer") == 1
    assert house_from_sign("Cancer", "Leo") == 2
    assert house_from_sign("Cancer", "Aries") == 10


def test_all_houses():

    houses = build_whole_sign_houses("Aries")

    assert len(houses) == 12
    assert houses[1]["sign"] == "Aries"
    assert houses[2]["sign"] == "Taurus"
    assert houses[12]["sign"] == "Pisces"


def test_planet_mapping():

    planets = {
        "Sun": {
            "sign": "Leo"
        },
        "Moon": {
            "sign": "Scorpio"
        },
        "Mars": {
            "sign": "Aries"
        },
    }

    result = build_d1_whole_sign(
        "Cancer",
        planets
    )

    assert result["planet_house_mapping"]["Sun"] == 2
    assert result["planet_house_mapping"]["Moon"] == 5
    assert result["planet_house_mapping"]["Mars"] == 10
