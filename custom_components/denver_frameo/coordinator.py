from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .adb import FrameoADB
from .const import SCAN_INTERVAL


class FrameoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.adb = FrameoADB(
            entry.data["host"],
            entry.data["port"],
        )

        super().__init__(
            hass,
            logger=None,
            name="Denver Frameo Photoframe",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            await self.adb.connect()
        except Exception:
            pass

        raw = await self.adb.read_led_state()

        raw = raw.strip("<>")

        br, r, g, b = map(int, raw.split(","))

        return {
            "brightness": br,
            "rgb": (r, g, b),
            "is_on": br > 0,
        }
