from fastapi import FastAPI
import swisseph as swe

app = FastAPI()

# Vedic Astrology ke liye Lahiri Ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

@app.post("/calculate_kundli")
def calculate_kundli(data: dict):
    year = int(data.get("year"))
    month = int(data.get("month"))
    day = int(data.get("day"))
    hour = float(data.get("hour")) # e.g. 14.5 for 2:30 PM
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))

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
