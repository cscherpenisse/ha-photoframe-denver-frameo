from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .device import get_device_info


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data["denver_frameo"][
        entry.entry_id
    ]

    async_add_entities([
        FrameoAvailabilitySensor(coordinator)
    ])


class FrameoAvailabilitySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):
    _attr_name = "Frameo Online"

    _attr_device_class = "connectivity"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

    @property
    def is_on(self):
        return self.coordinator.data.get(
            "available",
            False,
        )
