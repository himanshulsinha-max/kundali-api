# astro_config.py

import swisseph as swe


# Vedic astrology standard used by this project
AYANAMSHA = swe.SIDM_LAHIRI


def configure_sidereal():
    """
    Configure Swiss Ephemeris for sidereal calculations.
    Must be called before calculating Lagna or planets.
    """
    swe.set_sid_mode(AYANAMSHA)
