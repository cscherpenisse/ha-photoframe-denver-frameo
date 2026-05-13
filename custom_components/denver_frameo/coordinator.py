import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .adb import FrameoADB
from .const import SCAN_INTERVAL


LOGGER = logging.getLogger(__name__)


class FrameoCoordinator(DataUpdateCoordinator):
    """Coordinator for Denver Frameo."""

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

    async def _async_update_data(self):
        """Fetch data from Frameo."""

        try:
            await self.adb.ensure_connected()

            # -------------------------
            # LED STATE
            # -------------------------

            raw = await self.adb.read_led_state()

            raw = raw.strip("<>")

            br, r, g, b = map(
                int,
                raw.split(","),
            )

            # -------------------------
            # SCREEN BRIGHTNESS
            # -------------------------

            screen_brightness = (
                await self.adb.get_screen_brightness()
            )

            return {
                "brightness": br,
                "rgb": (r, g, b),
                "is_on": br > 0,
                "screen_brightness": (
                    screen_brightness
                ),
            }

        except Exception as err:
            LOGGER.error(
                "Failed to update Frameo data: %s",
                err,
            )

            # Safe fallback state
            return {
                "brightness": 0,
                "rgb": (0, 0, 0),
                "is_on": False,
                "screen_brightness": 127,
            }
