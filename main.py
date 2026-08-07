from fastapi import FastAPI
from pydantic import BaseModel
import swisseph as swe

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

    sun_pos = swe.calc_ut(julian_day, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon_pos = swe.calc_ut(julian_day, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    return {
        "status": "success",
        "sun_degree": round(sun_pos, 2),
        "moon_degree": round(moon_pos, 2),
        "sun_sign_id": int(sun_pos // 30) + 1,
        "moon_sign_id": int(moon_pos // 30) + 1
    }
