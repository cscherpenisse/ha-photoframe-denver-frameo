import importlib

from .coordinator import FrameoCoordinator

DOMAIN = "denver_frameo"

PLATFORMS = [
    "light",
    "switch",
    "sensor",
    "button",
    "media_player",
]


async def async_setup_entry(hass, entry):
    """Setup Denver Frameo entry."""

    # Preload platforms to avoid blocking import warnings
    for platform in PLATFORMS:
        importlib.import_module(
            f".{platform}",
            package=__package__,
        )

    coordinator = FrameoCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[
        entry.entry_id
    ] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass, entry):
    """Unload Denver Frameo entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
