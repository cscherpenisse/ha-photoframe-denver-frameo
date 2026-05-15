from datetime import timedelta
import hashlib
import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.util.dt import utcnow

from .const import DOMAIN
from .device import get_device_info

LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup media player."""

    coordinator = hass.data[DOMAIN][
        entry.entry_id
    ]

    async_add_entities(
        [
            FrameoMediaPlayer(
                coordinator
            )
        ]
    )


class FrameoMediaPlayer(
    MediaPlayerEntity,
):
    """Denver Frameo media player."""

    _attr_name = "Screen"

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON |
        MediaPlayerEntityFeature.TURN_OFF
    )

    _attr_should_poll = True

    def __init__(
        self,
        coordinator,
    ):
        """Init."""

        self.coordinator = coordinator
        
        self._attr_state = MediaPlayerState.OFF
        
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_media"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

        self._media_image = (
            None,
            None,
        )

        self._attr_media_image_hash = None

        self._last_screencap = None

        self._available = True

    # --------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )

    # --------------------------------------------------
    # STATE
    # --------------------------------------------------

    @property
    def state(self):
        return self._state
        
    # --------------------------------------------------
    # MEDIA IMAGE
    # --------------------------------------------------

    async def async_get_media_image(
        self,
    ):
        """Return cached image."""

        return self._media_image

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    async def async_update(self):
        """Update media player."""

        if not self.available:
            return

        try:
            await self.coordinator.adb.ensure_connected()
            
            # ---------------------------------
            # SCREEN STATE
            # ---------------------------------

            screen_on = (
                await self.coordinator.adb.is_screen_on()
            )

            if screen_on:
                self._state = MediaPlayerState.ON
            else:
                self._state = MediaPlayerState.OFF
            
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
            # SAVE IMAGE
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
    # TURN ON/OFF
    # --------------------------------------------------

    async def async_turn_on(self):
        """Turn screen on."""

        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        """Turn screen off."""

        await self.coordinator.adb.toggle_screen()

    # --------------------------------------------------
    # EXTRA ATTRIBUTES
    # --------------------------------------------------
    
    @property
    def extra_state_attributes(self):
        """Extra attributes."""

        return {
            "foreground_app": self.coordinator.data.get(
                "foreground_app"
            ),
            "ip_address": self.coordinator.config_entry.data.get(
                "host"
            ),
        }
