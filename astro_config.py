# astro_config.py

import swisseph as swe


# Primary sidereal zodiac configuration
AYANAMSHA = swe.SIDM_LAHIRI


def configure_sidereal():
    """
    Configure Swiss Ephemeris for Lahiri sidereal calculations.
    """
    swe.set_sid_mode(AYANAMSHA)
