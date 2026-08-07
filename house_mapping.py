def calculate_house_mapping(planets, houses):

    result = {}

    house_cusps = []

    for i in range(12):
        house_cusps.append(houses[f"House_{i+1}"]["longitude"])

    for planet, data in planets.items():

        longitude = data["longitude"]

        house_number = 12

        for i in range(12):

            start = house_cusps[i]
            end = house_cusps[(i + 1) % 12]

            if end < start:
                end += 360

            check_longitude = longitude

            if check_longitude < start:
                check_longitude += 360

            if start <= check_longitude < end:
                house_number = i + 1
                break

        result[planet] = house_number

    return result
