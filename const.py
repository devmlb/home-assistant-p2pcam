"""Constants for P2PCam integration"""

from homeassistant.const import Platform

DOMAIN = "p2pcam"
PLATFORMS: list[Platform] = [Platform.CAMERA, Platform.SWITCH]

CONF_NAME = "name"
CONF_DEVICE_ID = "device_id"
CONF_HOST_IP = "host_ip"
CONF_CAM_IP = "camera_ip"
CONF_HORIZONTAL_FLIP = "horizontal_flip"
CONF_VERTICAL_FLIP = "vertical_flip"
