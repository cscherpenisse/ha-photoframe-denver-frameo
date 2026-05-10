from .const import DOMAIN, NAME, MANUFACTURER, MODEL


def get_device_info(entry):
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": NAME,
        "manufacturer": MANUFACTURER,
        "model": MODEL,
    }
