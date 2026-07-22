"""Implements the P2PCam camera component"""


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME
from homeassistant.components.camera import Camera
import p2pcam
import logging
import threading
import time
from .const import DOMAIN, CONF_CAMERA_IP, ATTR_HORIZONTAL, ATTR_VERTICAL, ATTR_TIMESTAMP


_LOGGER = logging.getLogger(__name__)


class P2PCamera(Camera):
    def __init__(self, cam_id: str, cam_name: str, camera_ip: str) -> None:
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
        self._ip = camera_ip
        
        self._client = None
        # Image buffer for real time streaming
        self._latest_image = None
        self._image_lock = threading.Lock()
        self._stop_thread = False
        self._attr_available = True
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

        while not self._stop_thread:
            try:
                self._client = p2pcam.LanVideoClient(self._ip)
                for frame in self._client.stream(timeout=5):
                    if self._stop_thread:
                        break
                    
                    if not self._attr_available:
                        self._attr_available = True
                        self.schedule_update_ha_state()
                    
                    with self._image_lock:
                        self._latest_image = frame
                
                if not self._stop_thread:
                    # Timeout reached, let the camera breathe a little 
                    # before trying to reconnect
                    self._attr_available = False
                    self.schedule_update_ha_state()
                    time.sleep(15)
            finally:
                if self._client:
                    try:
                        self._client.close()
                    finally:
                        self._client = None

    def camera_image(self, width=None, height=None) -> bytes | None:
        """Return the latest available image from the camera"""

        with self._image_lock:
            return self._latest_image

    def __del__(self) -> None:
        """"Properly stop the loop image retrieval"""

        self._stop_thread = True
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
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
        P2PCamera(entry.entry_id, data[CONF_NAME], data[CONF_CAMERA_IP])
    ])
