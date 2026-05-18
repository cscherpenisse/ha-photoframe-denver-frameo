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
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.BROWSE_MEDIA
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
    # MEDIA INFO
    # --------------------------------------------------

    @property
    def media_title(self):
        """Current track title."""

        return self.coordinator.data.get(
            "media_title"
        )

    @property
    def media_artist(self):
        """Current artist."""

        return self.coordinator.data.get(
            "media_artist"
        )

    @property
    def media_album_name(self):
        """Current album."""

        return self.coordinator.data.get(
            "media_album"
        )

    @property
    def app_name(self):
        """Current media app."""

        return self.coordinator.data.get(
            "media_app"
        )

    @property
    def media_content_type(self):
        """Media type."""

        return "image"

    @property
    def media_content_id(self):
        """Media id."""

        return "frameo_screen"

    @property
    def media_duration(self):
        return None

    @property
    def media_position(self):
        return None

    @property
    def media_position_updated_at(self):
        return None

    # --------------------------------------------------
    # SOURCE
    # --------------------------------------------------

    @property
    def source(self):
        """Current app."""

        return self.coordinator.data.get(
            "foreground_app"
        )

    @property
    def source_list(self):
        """Available apps."""

        return [
            "Frameo",
            "Fully Kiosk",
            "Spotify",
            "Screensaver",
        ]

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
    # MEDIA CONTROLS
    # --------------------------------------------------

    async def async_media_play(self):
        """Send play."""

        await self.coordinator.adb.shell(
            "input keyevent KEYCODE_MEDIA_PLAY"
        )

    async def async_media_pause(self):
        """Send pause."""

        await self.coordinator.adb.shell(
            "input keyevent KEYCODE_MEDIA_PAUSE"
        )

    async def async_media_stop(self):
        """Send stop."""

        await self.coordinator.adb.shell(
            "input keyevent KEYCODE_MEDIA_STOP"
        )

    # --------------------------------------------------
    # SOURCE SELECT
    # --------------------------------------------------

    async def async_select_source(
        self,
        source,
    ):
        """Launch app."""

        if source == "Frameo":
            await self.coordinator.adb.start_frameo()

        elif source == "Fully Kiosk":
            await self.coordinator.adb.start_fully_kiosk()

    # --------------------------------------------------
    # PLAY MEDIA
    # --------------------------------------------------

    async def async_play_media(
        self,
        media_type,
        media_id,
        **kwargs,
    ):
        """Optional play media support."""

        LOGGER.warning(
            "Play media requested: %s %s",
            media_type,
            media_id,
        )

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
            # DISPLAY SIZE
            # -------------------------

            "media_width": 1280,
            "media_height": 800,

            # -------------------------
            # DEBUG
            # -------------------------

            "ip_address": (
                self.coordinator.config_entry.data.get(
                    "host"
                )
            ),
        }
