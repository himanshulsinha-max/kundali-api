from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe

from planets import calculate_planets
from lagna import calculate_lagna
from houses import calculate_houses
from house_mapping import calculate_house_mapping
from nakshatra import calculate_all_nakshatras
from moon_balance import get_nakshatra_balance
from dasha import get_mahadasha
from core.time_engine import calculate_julian_day

from d1_whole_sign import build_d1_whole_sign
from planet_relationships import build_planet_relationships, get_sign_lord
from planet_aspects import build_aspect_engine
from yoga_engine import build_complete_yoga_analysis


app = FastAPI()


class KundliRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int = 0
    lat: float
    lon: float
    timezone: str


# Lahiri Ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)


@app.post("/calculate_kundli")
def calculate_kundli(data: KundliRequest):

    # -------------------------
    # Birth details
    # -------------------------
    year = data.year
    month = data.month
    day = data.day
    hour = data.hour
    minute = data.minute
    second = data.second
    lat = data.lat
    lon = data.lon
    timezone = data.timezone

    # -------------------------
    # Julian Day
    # -------------------------
    julian_day = calculate_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone
    )

    # -------------------------
    # Planetary positions
    # -------------------------
    planets = calculate_planets(julian_day)

    # -------------------------
    # Lagna
    # -------------------------
    lagna = calculate_lagna(
        julian_day,
        lat,
        lon
    )

    # -------------------------
    # Houses
    # -------------------------
    houses = calculate_houses(
        julian_day,
        lat,
        lon
    )

    # -------------------------
    # Planet → House mapping
    # -------------------------
    planet_house = calculate_house_mapping(
        planets,
        houses
    )

    # -------------------------
    # D1 Whole-Sign chart
    # -------------------------
    # This is the authoritative D1 mapping for Yoga/relationship logic.
    # The existing `houses` and `planet_house` outputs are retained for
    # backward compatibility with the current API.
    d1 = build_d1_whole_sign(
        lagna["sign"],
        planets
    )

    d1_houses = d1["houses"]
    d1_planet_house = d1["planet_house_mapping"]

    # House lord = lord of the sign occupying that Whole-Sign house.
    house_lords = {
        house_number: get_sign_lord(
            house_data["sign"]
        )
        for house_number, house_data in d1_houses.items()
    }

    # -------------------------
    # Planetary relationships
    # -------------------------
    relationship_data = build_planet_relationships(
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=d1_planet_house,
        lagna_sign=lagna["sign"],
    )

    # -------------------------
    # Graha Drishti / Aspects
    # -------------------------
    aspect_data = build_aspect_engine(planets)

    # -------------------------
    # Yoga detection + strength
    # -------------------------
    yoga_analysis = build_complete_yoga_analysis(
        planets=planets,
        house_lords=house_lords,
        planet_house_mapping=d1_planet_house,
        relationship_data=relationship_data,
        aspect_data=aspect_data,
        grah_data=None,
    )

    # -------------------------
    # Nakshatras
    # -------------------------
    nakshatras = calculate_all_nakshatras(
        planets
    )

    # -------------------------
    # Moon Nakshatra Balance
    # -------------------------
    moon_balance = get_nakshatra_balance(
        planets["Moon"]["longitude"]
    )

    # -------------------------
    # Vimshottari Mahadasha
    # -------------------------
    mahadasha = get_mahadasha(
        nakshatras["Moon"],
        moon_balance
    )

    # -------------------------
    # Final Response
    # -------------------------
    return {
        "status": "Success",

        # Core calculation layers
        "lagna": lagna,
        "planets": planets,
        "houses": houses,

        # Existing mapping retained for backward compatibility
        "planet_house": planet_house,

        # Authoritative D1 Whole-Sign layer for Vedic relationship/Yoga logic
        "d1": d1,
        "d1_planet_house": d1_planet_house,
        "house_lords": house_lords,

        # Relationship + Drishti data layers
        "planet_relationships": relationship_data,
        "planet_aspects": aspect_data,

        # Yoga detection + strength/affliction
        "yoga_analysis": yoga_analysis,

        # Existing timing layers
        "nakshatras": nakshatras,
        "moon_balance": moon_balance,
        "mahadasha": mahadasha,
    }
