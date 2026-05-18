from homeassistant.components.button import (
    ButtonEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .device import get_device_info


FULLY_KIOSK_PACKAGE = "de.ozerov.fully"

FRAMEO_PACKAGE = "com.frameo.app"


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup buttons."""

    coordinator = hass.data[
        "denver_frameo"
    ][entry.entry_id]

    async_add_entities(
        [
            StartFullyKioskButton(
                coordinator
            ),

            StartFrameoButton(
                coordinator
            ),

            FrameoRebootButton(
                coordinator
            ),
        ]
    )


# --------------------------------------------------
# START FULLY KIOSK
# --------------------------------------------------

class StartFullyKioskButton(
    CoordinatorEntity,
    ButtonEntity,
):
    """Start Fully Kiosk."""

    _attr_name = "Start Fully Kiosk"

    _attr_icon = "mdi:web"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_start_fully_kiosk"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    async def async_press(self):
        """Launch Fully Kiosk."""

        cmd = (
            "monkey -p de.ozerov.fully "
            "-c android.intent.category.LAUNCHER 1"
        )

        await self.coordinator.adb.shell(
            cmd
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )


# --------------------------------------------------
# START FRAMEO
# --------------------------------------------------

class StartFrameoButton(
    CoordinatorEntity,
    ButtonEntity,
):
    """Start Frameo app."""

    _attr_name = "Start Frameo"

    _attr_icon = "mdi:image-frame"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_start_frameo"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    async def async_press(self):
        """Launch Frameo."""

        cmd = (
            "monkey -p com.frameo.app "
            "-c android.intent.category.LAUNCHER 1"
        )

        await self.coordinator.adb.shell(
            cmd
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )


# --------------------------------------------------
# REBOOT
# --------------------------------------------------

class FrameoRebootButton(
    CoordinatorEntity,
    ButtonEntity,
):
    """Reboot Frameo."""

    _attr_name = "Reboot"

    _attr_icon = "mdi:restart"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_reboot"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    async def async_press(self):
        """Reboot Android."""

        await self.coordinator.adb.shell(
            "reboot"
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )
