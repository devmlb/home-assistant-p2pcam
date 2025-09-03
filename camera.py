"""Implements the P2PCam camera component"""
import logging

# import voluptuous as vol
# from homeassistant.const import CONF_NAME, CONF_HOST, CONF_IP_ADDRESS
# from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
# # import homeassistant.helpers.config_validation as cv

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.camera import Camera
from homeassistant.helpers.entity import DeviceInfo

import p2pcam as p2pcam_req

from .const import CONF_NAME, CONF_DEVICE_ID, CONF_CAM_IP, CONF_HOST_IP, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Configuration des entités sensor à partir de la configuration
    ConfigEntry passée en argument"""

    _LOGGER.debug("Calling async_setup_entry entry=%s", config)

    entity = P2PCam(hass, config)
    async_add_entities([entity], True)


class P2PCam(Camera):
    def __init__(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        config: ConfigEntry
    ) -> None:
        super().__init__()  # <-- Ajout : initialise Camera correctement
        self.hass = hass
        self._attr_name = config.data.get(CONF_NAME)
        self._device_id = config.entry_id
        self._attr_unique_id = self._device_id
        self._attr_has_entity_name = True
        self._host_ip = config.data.get(CONF_HOST_IP)
        self._target_ip = config.data.get(CONF_CAM_IP)

        self.camera = p2pcam_req.P2PCam(self._host_ip, self._target_ip)

    async def async_camera_image(self, width=0, height=0):
        """Retourne une image de la caméra (méthode asynchrone)."""
        # Si retrieveImage est synchrone, utiliser hass.async_add_executor_job
        return await self.hass.async_add_executor_job(self.camera.retrieveImage)

    @property
    def name(self):
        """Retourne le nom de la caméra."""
        return self._attr_name

    @property
    def unique_id(self):
        """Retourne l'identifiant unique de la caméra."""
        return self._attr_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_id,
            manufacturer="P2PCam",
            model=DOMAIN,
        )
