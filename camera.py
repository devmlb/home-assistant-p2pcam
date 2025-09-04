"""Implements the P2PCam camera component"""


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME
from homeassistant.components.camera import Camera
from p2pcam import P2PCam
import logging
import threading
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
        self._cam.NB_FRAGMENTS_TO_ACCUMULATE = 20
        # Image buffer for real time streaming
        self._latest_image = None
        self._image_lock = threading.Lock()
        self._stop_thread = False
        self._thread = threading.Thread(target=self._update_image_loop, daemon=True)
        self._thread.start()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device infos"""

        return DeviceInfo(
            identifiers={(DOMAIN, self._cam_id)},
            name=self._device_id,
            manufacturer=DOMAIN,
            model=self._device_id,
        )

    def _update_image_loop(self) -> None:
        """Continuously retrieve the latest image from the camera"""

        # We must use this loop because if several devices stream the camera feed
        # at the same time, Home Assistant runs image retrieval in parallel which
        # overloads the camera and causes the feed to stop
        # The following code allows us to use a single image retrieval loop and store
        # the latest available image which will then be distributed to all devices
        while not self._stop_thread:
            try:
                # Setting a few parameters before taking the photo
                self._cam.horizontal_flip = self._attrs[ATTR_HORIZONTAL]
                self._cam.vertical_flip = self._attrs[ATTR_VERTICAL]
                self._cam.add_timestamp = self._attrs[ATTR_TIMESTAMP]
                # Image capture
                image = self._cam.retrieveImage()
                # Storing the latest image
                with self._image_lock:
                    self._latest_image = image
            except Exception as e:
                _LOGGER.error("Cannot retrieve the video stream from the camera: %s", e)

    def camera_image(self, width=None, height=None) -> bytes | None:
        """Return the latest available image from the camera"""

        with self._image_lock:
            return self._latest_image

    def __del__(self) -> None:
        """"Properly stop the loop image retrieval"""

        self._stop_thread = True
        if hasattr(self, "_thread"):
            self._thread.join(timeout=1)


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
