from .coordinator import FrameoCoordinator

PLATFORMS = [ "light", "switch", "sensor", "button", "media_player", "number", "binary_sensor", ]


async def async_setup_entry(hass, entry):
    coordinator = FrameoCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("denver_frameo", {})[entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_send_command(call):
        command = call.data["command"]

        await coordinator.adb.shell(command)


    hass.services.async_register(
        DOMAIN,
        "send_command",
        handle_send_command,
    )

    return True


async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data["denver_frameo"].pop(entry.entry_id)

    return unload_ok
