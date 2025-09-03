"""Constants for P2PCam integration"""

from homeassistant.const import Platform

DOMAIN = "p2pcam"
PLATFORMS: list[Platform] = [Platform.CAMERA, Platform.SWITCH]

CONF_NAME = "name"
CONF_DEVICE_ID = "device_id"
CONF_HOST_IP = "host_ip"
CONF_CAMERA_IP = "camera_ip"

ATTR_HORIZONTAL = "horizontal_flip"
ATTR_VERTICAL = "vertical_flip"
ATTR_TIMESTAMP = "add_timestamp"
