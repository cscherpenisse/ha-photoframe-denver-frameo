from datetime import timedelta
import hashlib
import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)

from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)

from .const import DOMAIN
from .device import get_device_info

LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup media player."""

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            FrameoMediaPlayer(
                coordinator
            )
        ],
        True,
    )


class FrameoMediaPlayer(
    MediaPlayerEntity
):
    """Denver Frameo media player."""

    _attr_name = "Frameo Screen"

    _attr_should_poll = True

    _attr_media_image_remotely_accessible = False

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )

    # --------------------------------------------------
    # INIT
    # --------------------------------------------------

    def __init__(
        self,
        coordinator,
    ):
        """Init."""

        self.coordinator = coordinator

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

    # --------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------

    @property
    def available(self):
        """Return availability."""

        data = self.coordinator.data or {}

        return data.get(
            "available",
            False,
        )

    # --------------------------------------------------
    # STATE
    # --------------------------------------------------

    @property
    def state(self):
        """Return media player state."""

        data = self.coordinator.data or {}

        if not data.get(
            "available",
            False,
        ):
            return STATE_UNAVAILABLE

        if data.get(
            "screen_on",
            False,
        ):
            return STATE_ON

        return STATE_OFF

    # --------------------------------------------------
    # MEDIA TITLE
    # --------------------------------------------------

    @property
    def media_title(self):
        """Current track title."""

        return self.coordinator.data.get(
            "media_title"
        )

    # --------------------------------------------------
    # MEDIA ARTIST
    # --------------------------------------------------

    @property
    def media_artist(self):
        """Current artist."""

        return self.coordinator.data.get(
            "media_artist"
        )

    # --------------------------------------------------
    # MEDIA ALBUM
    # --------------------------------------------------

    @property
    def media_album_name(self):
        """Current album."""

        return self.coordinator.data.get(
            "media_album"
        )

    # --------------------------------------------------
    # APP NAME
    # --------------------------------------------------

    @property
    def app_name(self):
        """Current media app."""

        return self.coordinator.data.get(
            "media_app"
        )

    # --------------------------------------------------
    # MEDIA IMAGE
    # --------------------------------------------------

    async def async_get_media_image(
        self,
    ):
        """Return current screenshot."""

        return self._media_image

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    async def async_update(self):
        """Update from coordinator."""

        try:
            await self.coordinator.async_request_refresh()

            data = self.coordinator.data or {}

            image = data.get(
                "screenshot"
            )

            if image:
                self._media_image = (
                    image,
                    "image/png",
                )

                self._attr_media_image_hash = (
                    hashlib.sha256(
                        image
                    ).hexdigest()[:16]
                )

        except Exception as err:
            LOGGER.warning(
                "Media update failed: %s",
                err,
            )

    # --------------------------------------------------
    # TURN ON
    # --------------------------------------------------

    async def async_turn_on(self):
        """Turn screen on."""

        if not self.coordinator.data.get(
            "screen_on",
            False,
        ):
            await self.coordinator.adb.toggle_screen()

            await self.coordinator.async_request_refresh()

    # --------------------------------------------------
    # TURN OFF
    # --------------------------------------------------

    async def async_turn_off(self):
        """Turn screen off."""

        if self.coordinator.data.get(
            "screen_on",
            False,
        ):
            await self.coordinator.adb.toggle_screen()

            await self.coordinator.async_request_refresh()

    # --------------------------------------------------
    # EXTRA ATTRIBUTES
    # --------------------------------------------------

    @property
    def extra_state_attributes(self):
        """Extra attributes."""

        data = self.coordinator.data or {}

        return {
            # -------------------------
            # SCREEN
            # -------------------------

            "screen_on": data.get(
                "screen_on",
                False,
            ),

            "display_state": data.get(
                "display_state",
                "OFF",
            ),

            "screen_brightness": data.get(
                "screen_brightness",
                127,
            ),

            # -------------------------
            # APPS
            # -------------------------

            "foreground_app": data.get(
                "foreground_app",
                "unknown",
            ),

            "media_app": data.get(
                "media_app",
            ),

            # -------------------------
            # MEDIA
            # -------------------------

            "media_title": data.get(
                "media_title",
            ),

            "media_artist": data.get(
                "media_artist",
            ),

            "media_album": data.get(
                "media_album",
            ),

            # -------------------------
            # DEBUG
            # -------------------------

            "ip_address": (
                self.coordinator.config_entry.data.get(
                    "host"
                )
            ),

            # -------------------------
            # DISPLAY SIZE
            # -------------------------

            "media_width": 1280,
            "media_height": 800,
        }
