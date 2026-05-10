from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import FrameoCoordinator

async def async_setup_entry(hass, entry):
    coordinator = FrameoCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("denver_frameo", {})[entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setup(entry, "light")
    await hass.config_entries.async_forward_entry_setup(entry, "switch")
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")

    return True


async def async_unload_entry(hass, entry):
    unload_ok = True

    for platform in ("light", "switch", "sensor"):
        unload_ok &= await hass.config_entries.async_forward_entry_unload(
            entry, platform
        )

    if unload_ok:
        hass.data["denver_frameo"].pop(entry.entry_id)

    return unload_ok
