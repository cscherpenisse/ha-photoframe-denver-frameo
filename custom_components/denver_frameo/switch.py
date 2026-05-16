from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .device import get_device_info

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoScreenSwitch(coordinator)
    ])


class FrameoScreenSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "Frameo Screen"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = (f"{coordinator.config_entry.entry_id}_frameo_screen")
        ###self._attr_device_info = get_device_info(coordinator.config_entry)
        self._attr_device_info = (
                    get_device_info(
                        coordinator.config_entry
                    )
                )
    
    
    @property
    def is_on(self):
        return True

    async def async_turn_on(self, **kwargs):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.adb.toggle_screen()
