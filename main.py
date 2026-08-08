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


swe.set_sid_mode(swe.SIDM_LAHIRI)


@app.post("/calculate_kundli")
def calculate_kundli(data: KundliRequest):

    year = data.year
    month = data.month
    day = data.day
    hour = data.hour
    lat = data.lat
    lon = data.lon

    julian_day = swe.julday(year, month, day, hour)

    planets = calculate_planets(julian_day)

    lagna = calculate_lagna(
        julian_day,
        lat,
        lon
    )

    houses = calculate_houses(
        julian_day,
        lat,
        lon
    )

    planet_house = calculate_house_mapping(
        planets,
        houses
    )

    nakshatras = calculate_all_nakshatras(
        planets
    )

    mahadasha = get_mahadasha(
        nakshatras["Moon"]
    )

    moon_balance = get_nakshatra_balance(
        planets["Moon"]["longitude"]
    )

mahadasha = get_mahadasha(
    nakshatras["Moon"],
    moon_balance
)

return {
    "status":"Success",
    "lagna":lagna,
    "planets":planets,
    "houses":houses,
    "planet_house":planet_house,
    "nakshatras":nakshatras,
    "mahadasha":mahadasha
}
