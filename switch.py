"""Implements the P2PCam settings components"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo

import p2pcam as p2pcam_req

from .const import CONF_NAME, CONF_DEVICE_ID, CONF_CAM_IP, CONF_HOST_IP, DOMAIN, CONF_HORIZONTAL_FLIP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Configuration des entités sensor à partir de la configuration
    ConfigEntry passée en argument"""

    _LOGGER.debug("Calling async_setup_entry entry=%s", config)

    entity = P2PCamHorizontalFlip(hass, config)
    async_add_entities([entity], True)


class P2PCamHorizontalFlip(SwitchEntity):
    def __init__(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        config: ConfigEntry
    ) -> None:
        self.hass = hass
        self.config_entry = config
        self._device_id = config.entry_id
        self._attr_has_entity_name = True
        self._attr_name = "Flip horizontally"
        self._attr_icon = "mdi:flip-horizontal"
        self._attr_unique_id = self._device_id
        self._attr_is_on = config.data.get(CONF_HORIZONTAL_FLIP)

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        new_data = self.config_entry.data
        _LOGGER.debug(new_data)
        new_data.set(self.config_entry.data.get(CONF_HORIZONTAL_FLIP), True)
        self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)

    def turn_off(self, **kwargs):
        """Turn the entity off."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_id,
            manufacturer="P2PCam",
            model=DOMAIN,
        )
