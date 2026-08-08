from planet_strength import (
    get_dignity,
    is_moolatrikona,
    is_own_sign,
    get_natural_relationship,
)


def test_sun_exalted():

    result = get_dignity(
        "Sun",
        "Aries",
        10.0
    )

    assert result["dignity"] == "exalted"
    assert result["exalted"] is True


def test_sun_debilitated():

    result = get_dignity(
        "Sun",
        "Libra",
        10.0
    )

    assert result["dignity"] == "debilitated"
    assert result["debilitated"] is True


def test_mars_moolatrikona():

    assert is_moolatrikona(
        "Mars",
        "Aries",
        10.0
    ) is True


def test_mars_own_sign():

    assert is_own_sign(
        "Mars",
        "Scorpio"
    ) is True


def test_jupiter_moolatrikona():

    assert is_moolatrikona(
        "Jupiter",
        "Sagittarius",
        5.0
    ) is True


def test_saturn_debilitated():

    result = get_dignity(
        "Saturn",
        "Aries",
        20.0
    )

    assert result["debilitated"] is True


def test_friend_relationship():

    assert get_natural_relationship(
        "Sun",
        "Mars"
    ) == "friend"


def test_enemy_relationship():

    assert get_natural_relationship(
        "Sun",
        "Venus"
    ) == "enemy"


def test_neutral_relationship():

    assert get_natural_relationship(
        "Sun",
        "Mercury"
    ) == "neutral"
