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
        "lagna": lagna,
        "planets": planets,
        "houses": houses,
        "planet_house": planet_house,
        "nakshatras": nakshatras,
        "moon_balance": moon_balance,
        "mahadasha": mahadasha
    }
