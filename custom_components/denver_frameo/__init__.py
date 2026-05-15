from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .coordinator import FrameoCoordinator

PLATFORMS = [
    "light",
    "switch",
    "sensor",
    "button",
    "media_player",
    "number",
    "binary_sensor",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Denver Frameo."""

    coordinator = FrameoCoordinator(
        hass,
        entry,
    )

    # --------------------------------------------------
    # FIRST REFRESH
    # --------------------------------------------------

    await coordinator.async_config_entry_first_refresh()

    # --------------------------------------------------
    # STORE COORDINATOR
    # --------------------------------------------------

    hass.data.setdefault(
        DOMAIN,
        {}
    )

    hass.data[DOMAIN][
        entry.entry_id
    ] = coordinator

    # --------------------------------------------------
    # LOAD PLATFORMS
    # --------------------------------------------------

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    # --------------------------------------------------
    # SERVICE: SEND COMMAND
    # --------------------------------------------------

    async def handle_send_command(
        call: ServiceCall,
    ):
        """Send raw ADB command."""

        command = call.data.get(
            "command"
        )

        if not command:
            raise HomeAssistantError(
                "Missing command"
            )

        try:
            await coordinator.adb.ensure_connected()

            response = await coordinator.adb.shell(
                command
            )

            return {
                "success": True,
                "response": response,
            }

        except Exception as err:
            raise HomeAssistantError(
                f"ADB command failed: {err}"
            ) from err

    # --------------------------------------------------
    # REGISTER SERVICE
    # --------------------------------------------------

    if not hass.services.has_service(
        DOMAIN,
        "send_command",
    ):
        hass.services.async_register(
            DOMAIN,
            "send_command",
            handle_send_command,
            supports_response=True,
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Denver Frameo."""

    unload_ok = (
        await hass.config_entries.async_unload_platforms(
            entry,
            PLATFORMS,
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

    return unload_ok
