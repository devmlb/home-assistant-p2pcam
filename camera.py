"""Implements the P2PCam camera component"""


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME
from homeassistant.components.camera import Camera
from p2pcam import P2PCam
import logging
from .const import DOMAIN, CONF_HOST_IP, CONF_CAMERA_IP, ATTR_HORIZONTAL, ATTR_VERTICAL, ATTR_TIMESTAMP


_LOGGER = logging.getLogger(__name__)


class P2PCamera(Camera):
    def __init__(self, cam_id: str, cam_name: str, host_ip: str, camera_ip: str) -> None:
        super().__init__()
        # Home Assistant attributes
        self._attr_has_entity_name = True
        self._attr_name = "Stream"
        self._device_id = cam_name
        self._attr_unique_id = cam_id
        self._attr_icon = "mdi:video"
        # Custom attributes
        self._attrs = {
            ATTR_HORIZONTAL: False,
            ATTR_VERTICAL: False,
            ATTR_TIMESTAMP: False,
        }
        self._cam_id = cam_id
        # P2PCam object
        self._cam = P2PCam(host_ip, camera_ip)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device infos"""

        return DeviceInfo(
            identifiers={(DOMAIN, self._cam_id)},
            name=self._device_id,
            manufacturer=DOMAIN,
            model=self._device_id,
        )

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        """Return an image taken from the camera"""

        return await self.hass.async_add_executor_job(self._get_image)

    def _get_image(self) -> bytes | None:
        """Return an image retrieved by the P2PCam module"""

        # Set some settings before taking the picture
        self._cam.horizontal_flip = self._attrs[ATTR_HORIZONTAL]
        self._cam.vertical_flip = self._attrs[ATTR_VERTICAL]
        self._cam.add_timestamp = self._attrs[ATTR_TIMESTAMP]

        return self._cam.retrieveImage()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add the camera entity from the entry"""

    # Getting configuration data from hass
    data = hass.data[DOMAIN][entry.entry_id]

    # Add an entity
    async_add_entities([
        P2PCamera(entry.entry_id, data[CONF_NAME], data[CONF_HOST_IP], data[CONF_CAMERA_IP])
    ])
