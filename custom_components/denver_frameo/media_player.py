from datetime import datetime, timedelta
import hashlib
import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util.dt import utcnow

from .const import DOMAIN
from .device import get_device_info

LOGGER = logging.getLogger(__name__)

SCREENSHOT_INTERVAL = 15


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][
        entry.entry_id
    ]

    async_add_entities([
        FrameoMediaPlayer(
            coordinator
        )
    ])


class FrameoMediaPlayer(
    CoordinatorEntity,
    MediaPlayerEntity,
):
    """Denver Frameo media player."""

    _attr_name = "Screen"

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON +
        MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_media"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

        self._attr_state = (
            MediaPlayerState.ON
        )

        self._media_image = (
            None,
            None,
        )

        self._attr_media_image_hash = None

        self._last_screencap = None

        self._screencap_delta = (
            timedelta(
                seconds=SCREENSHOT_INTERVAL
            )
        )

    # --------------------------------------------------
    # STATE
    # --------------------------------------------------

    @property
    def state(self):
        if self.coordinator.data.get(
            "available",
            False,
        ):
            return MediaPlayerState.ON

        return MediaPlayerState.OFF

    # --------------------------------------------------
    # MEDIA IMAGE
    # --------------------------------------------------

    async def async_get_media_image(
        self,
    ):
        return self._media_image

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    async def async_update(self):
        """Update screenshot."""

        if not self.available:
            return

        time_elapsed = (
            self._last_screencap is None
            or (
                utcnow()
                - self._last_screencap
            ) >= self._screencap_delta
        )

        if not time_elapsed:
            return

        self._last_screencap = utcnow()

        try:
            # ---------------------------------
            # CREATE SCREENSHOT
            # ---------------------------------

            await self.coordinator.adb.create_screenshot()

            # ---------------------------------
            # READ SCREENSHOT
            # ---------------------------------

            data = (
                await self.coordinator.adb.read_screenshot()
            )

            # ---------------------------------
            # CACHE IMAGE
            # ---------------------------------

            if data:
                self._media_image = (
                    data,
                    "image/png",
                )

                self._attr_media_image_hash = (
                    hashlib.sha256(
                        data
                    ).hexdigest()[:16]
                )

        except Exception as err:
            LOGGER.debug(
                "Screenshot failed: %s",
                err,
            )

    # --------------------------------------------------
    # POWER
    # --------------------------------------------------

    async def async_turn_on(self):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        await self.coordinator.adb.toggle_screen()
