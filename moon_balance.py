NAKSHATRA_SIZE = 13.333333333333334


def get_nakshatra_balance(moon_longitude):

    position = moon_longitude % NAKSHATRA_SIZE

    remaining = NAKSHATRA_SIZE - position

    balance = remaining / NAKSHATRA_SIZE

    return balance
