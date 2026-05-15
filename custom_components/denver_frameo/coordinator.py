import asyncio
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    # --------------------------------------------------
    # MAIN UPDATE LOOP
    # --------------------------------------------------

    async def _async_update_data(self):
        """Fetch device state safely."""

        brightness = 0
        rgb = (0, 0, 0)
        screen_brightness = 127
        foreground_app = "unknown"
        available = False
        screen_on = False
        screenshot = None

        # ---------------------------------
        # CONNECT SAFELY
        # ---------------------------------

        try:
            await asyncio.wait_for(
                self.adb.ensure_connected(),
                timeout=5,
            )
            available = True

        except Exception as err:
            LOGGER.debug("ADB connect failed: %s", err)
            return {
                "brightness": 0,
                "rgb": (0, 0, 0),
                "is_on": False,
                "screen_brightness": 0,
                "foreground_app": "unknown",
                "available": False,
                "screen_on": False,
                "screenshot": None,
            }

        # ---------------------------------
        # LED STATE
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

        except Exception as err:
            LOGGER.debug("LED read failed: %s", err)

        # ---------------------------------
        # SCREEN STATE (CRUCIAL FOR MEDIA PLAYER)
        # ---------------------------------

        try:
            screen_on = await asyncio.wait_for(
                self.adb.is_screen_on(),
                timeout=3,
            )

        except Exception as err:
            LOGGER.debug("Screen state failed: %s", err)
            screen_on = False

        # ---------------------------------
        # SCREEN BRIGHTNESS
        # ---------------------------------

        try:
            screen_brightness = await asyncio.wait_for(
                self.adb.get_screen_brightness(),
                timeout=3,
            )

        except Exception as err:
            LOGGER.debug("Screen brightness failed: %s", err)

        # ---------------------------------
        # FOREGROUND APP
        # ---------------------------------

        try:
            foreground_app = await asyncio.wait_for(
                self.adb.get_foreground_app(),
                timeout=3,
            )

        except Exception as err:
            LOGGER.debug("Foreground app failed: %s", err)

        # ---------------------------------
        # SCREENSHOT (ONLY IF SCREEN ON)
        # ---------------------------------

        try:
            if screen_on:
                await asyncio.wait_for(
                    self.adb.create_screenshot(),
                    timeout=5,
                )

                screenshot = await asyncio.wait_for(
                    self.adb.read_screenshot(),
                    timeout=5,
                )

        except Exception as err:
            LOGGER.debug("Screenshot failed: %s", err)

        # ---------------------------------
        # FINAL STATE (ANDROIDTV STYLE)
        # ---------------------------------

        return {
            "brightness": brightness,
            "rgb": rgb,
            "is_on": brightness > 0,
            "screen_on": screen_on,
            "screen_brightness": screen_brightness,
            "foreground_app": foreground_app,
            "available": available,
            "screenshot": screenshot,
        }

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    async def _async_update_data_fallback(self):
        return {
            "brightness": 0,
            "rgb": (0, 0, 0),
            "is_on": False,
            "screen_on": False,
            "screen_brightness": 127,
            "foreground_app": "unknown",
            "available": False,
            "screenshot": None,
        }
