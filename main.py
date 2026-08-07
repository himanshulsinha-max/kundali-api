from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe
from planets import calculate_planets
from lagna import calculate_lagna

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
return {
    "status": "Success",
    "planets": planets
}
