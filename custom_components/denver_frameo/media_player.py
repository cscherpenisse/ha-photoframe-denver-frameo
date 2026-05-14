from __future__ import annotations
                coordinator.config_entry
            )
        )

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_media"
        )

        self._image = None

        self._last_image_update = None

        self._attr_media_image_remotely_accessible = (
            False
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
            return "on"

        return "off"

    # --------------------------------------------------
    # SCREENSHOT SUPPORT
    # --------------------------------------------------

    @property
    def media_image_url(self):
        return (
            f"/api/media_player_proxy/"
            f"{self.entity_id}"
        )

    async def async_get_media_image(self):
        """Return current screenshot."""

        try:
            await self.coordinator.adb.create_screenshot()

            image = await self.coordinator.adb.read_screenshot()

            if image:
                self._image = image

        except Exception:
            pass

        if self._image:
            return self._image, "image/png"

        return None, None

    # --------------------------------------------------
    # POWER CONTROL
    # --------------------------------------------------

    async def async_turn_on(self):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        await self.coordinator.adb.toggle_screen()
