import asyncio
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .adb import FrameoADB
from .const import SCAN_INTERVAL


LOGGER = logging.getLogger(__name__)


class FrameoCoordinator(DataUpdateCoordinator):
    """Coordinator for Denver Frameo photoframe."""

    def __init__(self, hass, entry):
        self.config_entry = entry

        self.adb = FrameoADB(
            entry.data["host"],
            entry.data["port"],
        )

        super().__init__(
            hass,
            LOGGER,
            name="Denver Frameo Photoframe",
            update_interval=timedelta(
                seconds=SCAN_INTERVAL
            ),
        )

    # --------------------------------------------------
    # MAIN UPDATE LOOP
    # --------------------------------------------------

    async def _async_update_data(self):
        """Fetch device state safely."""

        # ---------------------------------
        # DEFAULT STATE (IMPORTANT)
        # ---------------------------------

        brightness = 0
        rgb = (0, 0, 0)
        screen_brightness = 127
        foreground_app = "unknown"
        available = False

        # ---------------------------------
        # LED STATE (SAFE)
        # ---------------------------------

        try:
            raw = await asyncio.wait_for(
                self.adb.read_led_state(),
                timeout=3,
            )

            raw = raw.strip("<>")

            br, r, g, b = map(int, raw.split(","))

            brightness = br
            rgb = (r, g, b)
            available = True

        except Exception as err:
            LOGGER.debug(
                "LED read failed: %s",
                err,
            )

        # ---------------------------------
        # SCREEN BRIGHTNESS (SAFE)
        # ---------------------------------

        try:
            screen_brightness = await asyncio.wait_for(
                self.adb.get_screen_brightness(),
                timeout=3,
            )

        except Exception as err:
            LOGGER.debug(
                "Screen brightness failed: %s",
                err,
            )

        # ---------------------------------
        # FOREGROUND APP (SAFE + LIGHTWEIGHT)
        # ---------------------------------

        try:
            foreground_app = await asyncio.wait_for(
                self.adb.get_foreground_app(),
                timeout=3,
            )

        except Exception as err:
            LOGGER.debug(
                "Foreground app failed: %s",
                err,
            )

        # ---------------------------------
        # FINAL RETURN
        # ---------------------------------

        return {
            "brightness": brightness,
            "rgb": rgb,
            "is_on": brightness > 0,
            "screen_brightness": screen_brightness,
            "foreground_app": foreground_app,
            "available": available,
        }

    # --------------------------------------------------
    # SAFE FALLBACK
    # --------------------------------------------------

    async def _async_update_data_fallback(self):
        """Optional fallback state (not used by HA but useful conceptually)."""

        return {
            "brightness": 0,
            "rgb": (0, 0, 0),
            "is_on": False,
            "screen_brightness": 127,
            "foreground_app": "unknown",
            "available": False,
        }
