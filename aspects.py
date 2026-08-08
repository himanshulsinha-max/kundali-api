# aspects.py

PLANETS = [
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


# Classical Parashari Graha Drishti
# Every planet aspects the 7th from itself.
# Mars, Jupiter and Saturn have additional special aspects.
SPECIAL_ASPECTS = {
    "Mars": [4, 8],
    "Jupiter": [5, 9],
    "Saturn": [3, 10],
}


def validate_house(house):
    if not isinstance(house, int):
        raise TypeError("House must be an integer.")

    if not 1 <= house <= 12:
        raise ValueError(
            "House must be between 1 and 12."
        )


def target_house(source_house, aspect_distance):
    """
    Calculate the target house for a Graha Drishti.

    source_house = house occupied by planet
    aspect_distance = 3, 4, 5, 7, etc.
    """

    validate_house(source_house)

    if not isinstance(aspect_distance, int):
        raise TypeError(
            "Aspect distance must be an integer."
        )

    if not 1 <= aspect_distance <= 12:
        raise ValueError(
            "Aspect distance must be between 1 and 12."
        )

    return (
        (source_house - 1 + aspect_distance - 1)
        % 12
    ) + 1


def get_aspect_distances(planet):
    """
    Return all Graha Drishti distances for a planet.

    Current implementation:
        All planets -> 7th
        Mars -> 4th, 7th, 8th
        Jupiter -> 5th, 7th, 9th
        Saturn -> 3rd, 7th, 10th

    Rahu/Ketu currently use only 7th aspect.
    This remains configurable and can be changed
    when the project adopts a specific node convention.
    """

    distances = [7]

    distances.extend(
        SPECIAL_ASPECTS.get(planet, [])
    )

    return sorted(distances)


def get_planet_aspects(planet, source_house):
    """
    Return houses aspected by a planet.
    """

    validate_house(source_house)

    distances = get_aspect_distances(
        planet
    )

    aspects = []

    for distance in distances:

        aspects.append({
            "from_house": source_house,
            "distance": distance,
            "to_house": target_house(
                source_house,
                distance
            ),
        })

    return aspects


def build_aspects(planet_house_mapping):
    """
    Build Graha Drishti for all planets.

    Input:

        {
            "Sun": 1,
            "Moon": 2,
            "Mars": 4
        }

    Output:

        {
            "Sun": [...],
            "Moon": [...],
            "Mars": [...]
        }
    """

    if not isinstance(
        planet_house_mapping,
        dict
    ):
        raise TypeError(
            "planet_house_mapping must be a dictionary."
        )

    result = {}

    for planet, house in planet_house_mapping.items():

        result[planet] = get_planet_aspects(
            planet,
            house
        )

    return result
