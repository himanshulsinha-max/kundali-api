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
from planetary_strength import calculate_strength

from d1_whole_sign import build_d1_whole_sign
from planet_relationships import build_planet_relationships, get_sign_lord
from planet_aspects import build_aspect_engine
from yoga_engine import build_complete_yoga_analysis
from ashtakavarga import build_ashtakavarga
from divisional_charts import build_divisional_charts

from transits import get_transits
from transit_facts import get_transit_facts


app = FastAPI()


# ============================================================
# REQUEST MODELS
# ============================================================

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


class TransitRequest(BaseModel):
    # Natal / birth details
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    birth_second: int = 0
    birth_lat: float
    birth_lon: float
    birth_timezone: str

    # Date/time for which transit is required
    transit_year: int
    transit_month: int
    transit_day: int
    transit_hour: int
    transit_minute: int
    transit_second: int = 0
    transit_timezone: str


# ============================================================
# LAHIRI AYANAMSHA
# ============================================================

swe.set_sid_mode(swe.SIDM_LAHIRI)


# ============================================================
# NATAL KUNDLI
# ============================================================

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
    # Planetary Strength / Dignity
    # -------------------------
    planetary_strength = calculate_strength(planets)

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
    d1 = build_d1_whole_sign(
        lagna["sign"],
        planets
    )

    d1_houses = d1["houses"]
    d1_planet_house = d1["planet_house_mapping"]

    # -------------------------
    # House lords
    # -------------------------
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
    # Ashtakavarga
    # -------------------------
    ashtakavarga = build_ashtakavarga(
        planets=planets,
        lagna_sign=lagna["sign"],
    )

    # -------------------------
    # Divisional Charts
    # -------------------------
    divisional_charts = build_divisional_charts(
        planets=planets
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

        "d1": d1,
        "d1_planet_house": d1_planet_house,
        "house_lords": house_lords,

        "planet_relationships": relationship_data,
        "planet_aspects": aspect_data,

        "planetary_strength": planetary_strength,

        "yoga_analysis": yoga_analysis,

        "ashtakavarga": ashtakavarga,

        "divisional_charts": divisional_charts,

        "nakshatras": nakshatras,
        "moon_balance": moon_balance,
        "mahadasha": mahadasha,
    }


# ============================================================
# TRANSIT ENGINE
# ============================================================

@app.post("/calculate_transits")
def calculate_transits_endpoint(data: TransitRequest):

    # --------------------------------------------------------
    # 1. Calculate natal Julian Day
    # --------------------------------------------------------

    natal_julian_day = calculate_julian_day(
        data.birth_year,
        data.birth_month,
        data.birth_day,
        data.birth_hour,
        data.birth_minute,
        data.birth_second,
        data.birth_timezone
    )

    # --------------------------------------------------------
    # 2. Calculate natal planets
    # --------------------------------------------------------

    natal_planets = calculate_planets(
        natal_julian_day
    )

    # --------------------------------------------------------
    # 3. Calculate natal Lagna
    # --------------------------------------------------------

    natal_lagna = calculate_lagna(
        natal_julian_day,
        data.birth_lat,
        data.birth_lon
    )

    # --------------------------------------------------------
    # 4. Calculate transit Julian Day
    # --------------------------------------------------------

    transit_julian_day = calculate_julian_day(
        data.transit_year,
        data.transit_month,
        data.transit_day,
        data.transit_hour,
        data.transit_minute,
        data.transit_second,
        data.transit_timezone
    )

    # --------------------------------------------------------
    # 5. Swiss Ephemeris transit calculation
    # --------------------------------------------------------

    transit_planets = get_transits(
        transit_julian_day
    )

    # --------------------------------------------------------
    # 6. Build interpretation-neutral transit facts
    # --------------------------------------------------------

    transit_facts = get_transit_facts(
        transit_planets=transit_planets,
        natal_planets=natal_planets,
        lagna=natal_lagna,
    )

    # --------------------------------------------------------
    # 7. Final response
    # --------------------------------------------------------

    return {
        "status": "Success",

        "natal": {
            "lagna": natal_lagna,
            "planets": natal_planets,
        },

        "transit": {
            "julian_day": transit_julian_day,
            "planets": transit_planets,
        },

        "transit_facts": transit_facts,
    }
