import logging

import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_HOST, CONF_IP_ADDRESS
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "p2pcam"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_IP_ADDRESS): cv.string
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    async_add_entities([P2PCam(hass, config)])


class P2PCam(Camera):
    def __init__(self, hass, config):
        super().__init__()
        from .utils import P2PCamModule

        self._name = config.get(CONF_NAME)
        self._host_ip = config.get(CONF_HOST)
        self._target_ip = config.get(CONF_IP_ADDRESS)

        self.camera = P2PCamModule(self._host_ip, self._target_ip)

    async def async_camera_image(self, width=0, height=0):
        return self.camera.retrieveImage()

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name
