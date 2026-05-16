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
    """Stable coordinator for Denver Frameo."""

    def __init__(self, hass, entry):
        self.config_entry = entry

        self.adb = FrameoADB(
            entry.data["host"],
            entry.data["port"],
        )

        # ---------------------------------
        # LAST KNOWN GOOD STATE
        # ---------------------------------

        self._last_data = {
            "brightness": 0,
            "rgb": (0, 0, 0),
            "is_on": False,
            "screen_on": False,
            "display_state": "OFF",
            "screen_brightness": 127,
            "foreground_app": "unknown",
            "power_dump": "",
            "screenshot": None,
            "available": True,
        }

        # ---------------------------------
        # FAILURE COUNTER
        # ---------------------------------

        self._failed_updates = 0

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
        """Stable update loop."""

        data = dict(self._last_data)

        success = False

        # --------------------------------------------------
        # ENSURE CONNECTION
        # --------------------------------------------------

        try:
            await asyncio.wait_for(
                self.adb.ensure_connected(),
                timeout=10,
            )

        except Exception as err:
            LOGGER.warning(
                "ADB connect failed: %s",
                err,
            )

            self._failed_updates += 1

            # keep old state for a while
            if self._failed_updates < 5:
                return data

            data["available"] = False
            return data

        # --------------------------------------------------
        # LED STATE
        # --------------------------------------------------

        try:
            raw = await asyncio.wait_for(
                self.adb.read_led_state(),
                timeout=5,
            )

            raw = raw.strip("<>")

            br, r, g, b = map(
                int,
                raw.split(","),
            )

            data["brightness"] = br
            data["rgb"] = (r, g, b)
            data["is_on"] = br > 0

            success = True

        except Exception as err:
            LOGGER.debug(
                "LED read failed: %s",
                err,
            )

        # --------------------------------------------------
        # DISPLAY POWER
        # --------------------------------------------------

        try:
            power_dump = await asyncio.wait_for(
                self.adb.shell(
                    "dumpsys power | grep 'Display Power'"
                ),
                timeout=5,
            )

            power_dump = str(power_dump)

            data["power_dump"] = power_dump

            if "state=ON" in power_dump:
                data["screen_on"] = True
                data["display_state"] = "ON"

            elif "state=OFF" in power_dump:
                data["screen_on"] = False
                data["display_state"] = "OFF"

            success = True

        except Exception as err:
            LOGGER.debug(
                "Display state failed: %s",
                err,
            )

        # --------------------------------------------------
        # SCREEN BRIGHTNESS
        # --------------------------------------------------

        try:
            data["screen_brightness"] = (
                await asyncio.wait_for(
                    self.adb.get_screen_brightness(),
                    timeout=5,
                )
            )

        except Exception as err:
            LOGGER.debug(
                "Brightness read failed: %s",
                err,
            )

        # --------------------------------------------------
        # FOREGROUND APP
        # --------------------------------------------------

        try:
            data["foreground_app"] = (
                await asyncio.wait_for(
                    self.adb.get_foreground_app(),
                    timeout=5,
                )
            )

        except Exception as err:
            LOGGER.debug(
                "Foreground app failed: %s",
                err,
            )

        # --------------------------------------------------
        # SCREENSHOT
        # --------------------------------------------------

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
                data["screenshot"] = screenshot

        except Exception as err:
            LOGGER.debug(
                "Screenshot failed: %s",
                err,
            )

        # --------------------------------------------------
        # FINAL STATUS
        # --------------------------------------------------

        if success:
            data["available"] = True
            self._failed_updates = 0
        else:
            self._failed_updates += 1

            LOGGER.warning(
                "Partial update failed (%s)",
                self._failed_updates,
            )

            if self._failed_updates >= 5:
                data["available"] = False

        self._last_data = data

        return data
