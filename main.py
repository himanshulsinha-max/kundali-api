from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe

from planets import calculate_planets
from lagna import calculate_lagna
from houses import calculate_houses
from house_mapping import calculate_house_mapping
from nakshatra import calculate_all_nakshatras

app = FastAPI()


class KundliRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: float
    lat: float
    lon: float


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

    return {
    "status": "Success",
    "lagna": lagna,
    "planets": planets,
    "houses": houses,
    "planet_house": planet_house,
    "nakshatras": nakshatras
    }
