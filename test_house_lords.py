from house_lords import (
    get_sign_lord,
    get_house_lord,
    build_house_lords,
)


def test_sign_lords():

    assert get_sign_lord("Aries") == "Mars"
    assert get_sign_lord("Taurus") == "Venus"
    assert get_sign_lord("Cancer") == "Moon"
    assert get_sign_lord("Leo") == "Sun"
    assert get_sign_lord("Sagittarius") == "Jupiter"
    assert get_sign_lord("Capricorn") == "Saturn"


def test_cancer_lagna_house_lords():

    result = build_house_lords("Cancer")

    assert result[1]["sign"] == "Cancer"
    assert result[1]["lord"] == "Moon"

    assert result[2]["sign"] == "Leo"
    assert result[2]["lord"] == "Sun"

    assert result[4]["sign"] == "Libra"
    assert result[4]["lord"] == "Venus"

    assert result[7]["sign"] == "Capricorn"
    assert result[7]["lord"] == "Saturn"

    assert result[10]["sign"] == "Aries"
    assert result[10]["lord"] == "Mars"


def test_twelve_houses():

    result = build_house_lords("Cancer")

    assert len(result) == 12
