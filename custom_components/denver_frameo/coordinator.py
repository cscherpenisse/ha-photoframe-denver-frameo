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
        """Fetch all Frameo state."""

        # --------------------------------------------------
        # DEFAULT VALUES
        # --------------------------------------------------

        brightness = 0
        rgb = (0, 0, 0)

        screen_brightness = 127

        foreground_app = "unknown"

        available = False

        screen_on = False

        display_state = "OFF"

        power_dump = ""

        screenshot = None

        # --------------------------------------------------
        # TEST ADB CONNECTION
        # --------------------------------------------------

        try:
            await asyncio.wait_for(
                self.adb.shell(
                    "echo connected"
                ),
                timeout=5,
            )

            available = True

        except Exception as err:
            LOGGER.warning(
                "ADB unavailable: %s",
                err,
            )

        # --------------------------------------------------
        # DISPLAY POWER STATE
        # --------------------------------------------------

        if available:

            try:
                power_dump = await asyncio.wait_for(
                    self.adb.shell(
                        "dumpsys power | grep 'Display Power'"
                    ),
                    timeout=5,
                )

                power_dump = str(
                    power_dump
                ).strip()

                LOGGER.warning(
                    "POWER DUMP: %s",
                    power_dump,
                )

                if "state=ON" in power_dump:
                    screen_on = True
                    display_state = "ON"

                elif "state=OFF" in power_dump:
                    screen_on = False
                    display_state = "OFF"

            except Exception as err:
                LOGGER.warning(
                    "Display state failed: %s",
                    err,
                )

        # --------------------------------------------------
        # SCREENSHOT
        # --------------------------------------------------

        if available and screen_on:

            try:
                await asyncio.wait_for(
                    self.adb.create_screenshot(),
                    timeout=10,
                )

                screenshot = await asyncio.wait_for(
                    self.adb.read_screenshot(),
                    timeout=15,
                )

                if screenshot:
                    LOGGER.warning(
                        "Screenshot OK (%s bytes)",
                        len(screenshot),
                    )

            except Exception as err:
                LOGGER.warning(
                    "Screenshot failed: %s",
                    err,
                )

        # --------------------------------------------------
        # LED STATE
        # --------------------------------------------------

        if available:

            try:
                raw = await asyncio.wait_for(
                    self.adb.read_led_state(),
                    timeout=3,
                )

                raw = raw.strip("<>")

                br, r, g, b = map(
                    int,
                    raw.split(","),
                )

                brightness = br

                rgb = (
                    r,
                    g,
                    b,
                )

            except Exception as err:
                LOGGER.debug(
                    "LED read failed: %s",
                    err,
                )

        # --------------------------------------------------
        # SCREEN BRIGHTNESS
        # --------------------------------------------------

        if available:

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

        # --------------------------------------------------
        # FOREGROUND APP
        # --------------------------------------------------

        if available:

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

        # --------------------------------------------------
        # FINAL DATA
        # --------------------------------------------------

        return {
            "available": available,

            "brightness": brightness,

            "rgb": rgb,

            "is_on": brightness > 0,

            "screen_brightness": screen_brightness,

            "foreground_app": foreground_app,

            "screen_on": screen_on,

            "display_state": display_state,

            "power_dump": power_dump,

            "screenshot": screenshot,
        }

    # --------------------------------------------------
    # SAFE FALLBACK
    # --------------------------------------------------

    async def _async_update_data_fallback(self):
        """Fallback state."""

        return {
            "available": False,

            "brightness": 0,

            "rgb": (0, 0, 0),

            "is_on": False,

            "screen_brightness": 127,

            "foreground_app": "unknown",

            "screen_on": False,

            "display_state": "OFF",

            "power_dump": "",

            "screenshot": None,
        }
