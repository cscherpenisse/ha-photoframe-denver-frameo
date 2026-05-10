from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoScreenSwitch(coordinator)
    ])


class FrameoScreenSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "Frameo Screen"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def is_on(self):
        return True

    async def async_turn_on(self, **kwargs):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.adb.toggle_screen()
