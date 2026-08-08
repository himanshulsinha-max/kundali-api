from aspects import (
    target_house,
    get_aspect_distances,
    get_planet_aspects,
    build_aspects,
)


def test_seventh_aspect():

    assert target_house(1, 7) == 7
    assert target_house(5, 7) == 11
    assert target_house(10, 7) == 4


def test_mars_aspects():

    distances = get_aspect_distances("Mars")

    assert distances == [4, 7, 8]


def test_jupiter_aspects():

    distances = get_aspect_distances("Jupiter")

    assert distances == [5, 7, 9]


def test_saturn_aspects():

    distances = get_aspect_distances("Saturn")

    assert distances == [3, 7, 10]


def test_sun_aspect():

    distances = get_aspect_distances("Sun")

    assert distances == [7]


def test_mars_from_first_house():

    aspects = get_planet_aspects(
        "Mars",
        1
    )

    houses = [
        item["to_house"]
        for item in aspects
    ]

    assert houses == [4, 7, 8]


def test_jupiter_from_first_house():

    aspects = get_planet_aspects(
        "Jupiter",
        1
    )

    houses = [
        item["to_house"]
        for item in aspects
    ]

    assert houses == [5, 7, 9]


def test_saturn_from_first_house():

    aspects = get_planet_aspects(
        "Saturn",
        1
    )

    houses = [
        item["to_house"]
        for item in aspects
    ]

    assert houses == [3, 7, 10]


def test_wraparound():

    # 10th house + 7th aspect = 4th house
    assert target_house(10, 7) == 4


def test_complete_mapping():

    mapping = {
        "Sun": 1,
        "Mars": 4,
        "Jupiter": 5,
        "Saturn": 10,
    }

    result = build_aspects(mapping)

    assert result["Sun"][0]["to_house"] == 7

    mars_houses = [
        x["to_house"]
        for x in result["Mars"]
    ]

    assert mars_houses == [7, 10, 11]
