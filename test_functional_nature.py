from functional_nature import (
    get_house_lordships,
    get_functional_profile,
    build_functional_profiles,
)


def test_cancer_lagna_lordships():

    result = get_house_lordships(
        "Cancer"
    )

    assert result["Moon"] == [1]
    assert result["Sun"] == [2]
    assert result["Mercury"] == [3, 12]
    assert result["Venus"] == [4, 11]
    assert result["Mars"] == [5, 10]
    assert result["Jupiter"] == [6, 9]
    assert result["Saturn"] == [7, 8]


def test_cancer_lagna_mars():

    result = get_functional_profile(
        "Cancer",
        "Mars"
    )

    assert result["owned_houses"] == [5, 10]
    assert result["is_trikona_lord"] is True
    assert result["is_kendra_lord"] is True


def test_cancer_lagna_jupiter():

    result = get_functional_profile(
        "Cancer",
        "Jupiter"
    )

    assert result["owned_houses"] == [6, 9]
    assert result["is_dusthana_lord"] is True
    assert result["is_trikona_lord"] is True


def test_all_planets():

    result = build_functional_profiles(
        "Cancer"
    )

    assert len(result) == 7

    assert "Sun" in result
    assert "Moon" in result
    assert "Mars" in result
    assert "Mercury" in result
    assert "Jupiter" in result
    assert "Venus" in result
    assert "Saturn" in result
