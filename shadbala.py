"""BPHS-oriented Shadbala engine.

This module is intentionally staged. Swiss Ephemeris remains the source of
astronomical positions; source-sensitive Jyotish formulas are kept explicit.
"""
from __future__ import annotations
from typing import Any, Dict

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NAISARGIKA_BALA = {"Sun":60.0,"Moon":51.428571,"Venus":42.857143,"Jupiter":34.285714,"Mercury":25.714286,"Mars":17.142857,"Saturn":8.571429}
REQUIRED_BALA = {"Sun":390.0,"Moon":360.0,"Mars":300.0,"Mercury":420.0,"Jupiter":390.0,"Venus":330.0,"Saturn":300.0}
SAPTAVARGA_VALUES = {"exalted":45.0,"moolatrikona":30.0,"own_sign":20.0,"friendly_sign":15.0,"neutral_sign":10.0,"enemy_sign":4.0}

def _longitude(data: Dict[str, Any]) -> float:
    if "longitude" not in data: raise ValueError("Planet data requires longitude for Shadbala")
    return float(data["longitude"]) % 360.0

def angular_distance(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)

def uchcha_bala(planet: str, longitude: float, debilitation_longitude: float) -> float:
    if planet not in PLANETS: raise ValueError(f"Unsupported planet: {planet}")
    return round(angular_distance(longitude, debilitation_longitude) / 3.0, 6)

def _house_cusp_longitude(houses: Dict[str, Any], house_number: int) -> float:
    cusps = houses.get("cusps") or houses.get("house_cusps")
    if isinstance(cusps, dict):
        value = cusps.get(str(house_number), cusps.get(house_number))
        if value is not None: return float(value) % 360.0
    if isinstance(cusps, (list, tuple)) and len(cusps) >= house_number:
        return float(cusps[house_number - 1]) % 360.0
    raise ValueError("House cusps are required for Dig Bala")

def dig_bala(planet: str, longitude: float, houses: Dict[str, Any]) -> float:
    zero_house = {"Sun":4,"Mars":4,"Jupiter":7,"Mercury":7,"Moon":10,"Venus":10,"Saturn":1}[planet]
    return round(angular_distance(longitude, _house_cusp_longitude(houses, zero_house)) / 3.0, 6)

def naisargika_bala(planet: str) -> float: return NAISARGIKA_BALA[planet]
def kendradi_bala(house_number: int) -> float: return 60.0 if house_number in (1,4,7,10) else 30.0 if house_number in (2,5,8,11) else 15.0
def drik_bala(net_aspect_virupas: float) -> float: return float(net_aspect_virupas)
def total_to_rupas(total_virupas: float) -> float: return round(float(total_virupas) / 60.0, 6)
def strength_ratio(total_virupas: float, planet: str) -> float: return round(float(total_virupas) / REQUIRED_BALA[planet], 6)

def evaluate_strength(total_virupas: float, planet: str) -> Dict[str, Any]:
    required = REQUIRED_BALA[planet]
    return {"total_virupas":round(total_virupas,6),"total_rupas":total_to_rupas(total_virupas),"required_virupas":required,"required_rupas":total_to_rupas(required),"strength_ratio":strength_ratio(total_virupas,planet),"meets_required_bala":total_virupas >= required}

def calculate_shadbala(planets_data: Dict[str, Dict[str, Any]], houses: Dict[str, Any] | None = None, debilitation_longitudes: Dict[str, float] | None = None, house_numbers: Dict[str, int] | None = None, drik_values: Dict[str, float] | None = None, additional_bala: Dict[str, Dict[str, float]] | None = None) -> Dict[str, Dict[str, Any]]:
    houses = houses or {}; debilitation_longitudes = debilitation_longitudes or {}; house_numbers = house_numbers or {}; drik_values = drik_values or {}; additional_bala = additional_bala or {}; results = {}
    for planet in PLANETS:
        if planet not in planets_data: continue
        p = planets_data[planet]; components = {"naisargika_bala": naisargika_bala(planet)}
        if planet in debilitation_longitudes: components["uchcha_bala"] = uchcha_bala(planet, _longitude(p), debilitation_longitudes[planet])
        if houses and planet in house_numbers:
            components["dig_bala"] = dig_bala(planet, _longitude(p), houses); components["kendradi_bala"] = kendradi_bala(house_numbers[planet])
        if planet in drik_values: components["drik_bala"] = drik_bala(drik_values[planet])
        components.update(additional_bala.get(planet, {})); total = sum(components.values())
        results[planet] = {"planet":planet,"components":{k:round(v,6) for k,v in components.items()},"status":"partial" if len(components)<6 else "complete",**evaluate_strength(total,planet)}
    return results

def calculate_strength(planets_data: Dict[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Dict[str, Any]]:
    return calculate_shadbala(planets_data, **kwargs)
