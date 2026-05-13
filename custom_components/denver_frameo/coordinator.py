import asyncio
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .adb import FrameoADB
from .const import SCAN_INTERVAL


LOGGER = logging.getLogger(__name__)


class FrameoCoordinator(
    DataUpdateCoordinator
):
    """Coordinator for Denver Frameo."""

    def __init__(
        self,
        hass,
        entry,
    ):
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

    async def _async_update_data(self):
        """Fetch Frameo state."""

        try:
            # ---------------------------------
            # CONNECT WITH TIMEOUT
            # ---------------------------------

            try:
                await asyncio.wait_for(
                    self.adb.ensure_connected(),
                    timeout=5,
                )

            except asyncio.TimeoutError:
                LOGGER.warning(
                    "Frameo connection timeout"
                )

                return self._offline_state()

            # ---------------------------------
            # LED STATE
            # ---------------------------------

            raw = await self.adb.read_led_state()

            raw = raw.strip("<>")

            br, r, g, b = map(
                int,
                raw.split(","),
            )

            # ---------------------------------
            # SCREEN BRIGHTNESS
            # ---------------------------------

            screen_brightness = (
                await self.adb.get_screen_brightness()
            )

            # ---------------------------------
            # FOREGROUND APP
            # ---------------------------------

            foreground_app = (
                await self.adb.get_foreground_app()
            )

            # ---------------------------------
            # SUCCESS STATE
            # ---------------------------------

            return {
                "brightness": br,
                "rgb": (r, g, b),
                "is_on": br > 0,
                "screen_brightness": (
                    screen_brightness
                ),
                "foreground_app": (
                    foreground_app
                ),
                "available": True,
            }

        except asyncio.CancelledError:
            raise

        except Exception as err:
            LOGGER.error(
                "Failed to update Frameo data: %s",
                err,
            )

            return self._offline_state()

    # --------------------------------------------------
    # FALLBACK OFFLINE STATE
    # --------------------------------------------------

    def _offline_state(self):
        """Return safe offline state."""

        return {
            "brightness": 0,
            "rgb": (0, 0, 0),
            "is_on": False,
            "screen_brightness": 127,
            "foreground_app": "unknown",
            "available": False,
        }
