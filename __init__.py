"""Initialize the P2PCam integration package"""


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import logging
from .const import DOMAIN, PLATFORMS


_LOGGER = logging.getLogger(__name__)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Force the reloading of entities associated with a configEntry"""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Create entities from a configEntry"""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Each platform must complete the setup.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registration of the update_listener function
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Clean entry after unload"""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
