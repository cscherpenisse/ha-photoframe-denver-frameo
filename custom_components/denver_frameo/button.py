from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .device import get_device_info


FULLY_KIOSK_PACKAGE = "de.ozerov.fully"
FRAMEO_PACKAGE = "com.frameo.app"


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities(
        [
            StartFullyKioskButton(coordinator),
            StartFrameoButton(coordinator),
        ]
    )


class StartFullyKioskButton(CoordinatorEntity, ButtonEntity):
    _attr_name = "Start Fully Kiosk"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

    async def async_press(self):
        cmd = (
            "monkey -p de.ozerov.fully "
            "-c android.intent.category.LAUNCHER 1"
        )

        await self.coordinator.adb.shell(cmd)


class StartFrameoButton(CoordinatorEntity, ButtonEntity):
    _attr_name = "Start Frameo"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

    async def async_press(self):
        cmd = (
            "monkey -p com.frameo.app "
            "-c android.intent.category.LAUNCHER 1"
        )

        await self.coordinator.adb.shell(cmd)
