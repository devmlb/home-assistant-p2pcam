"""Implements the P2PCam settings components"""

from .const import DOMAIN, ATTR_HORIZONTAL, ATTR_VERTICAL, ATTR_TIMESTAMP
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
import logging

# from homeassistant.core import HomeAssistant
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo

# import p2pcam as p2pcam_req

# from .const import CONF_NAME, CONF_DEVICE_ID, CONF_CAM_IP, CONF_HOST_IP, DOMAIN, CONF_HORIZONTAL_FLIP

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback):
#     """Configuration des entités sensor à partir de la configuration
#     ConfigEntry passée en argument"""

#     _LOGGER.debug("Calling async_setup_entry entry=%s", config)

#     entity = P2PCamHorizontalFlip(hass, config)
#     async_add_entities([entity], True)


# class P2PCamHorizontalFlip(SwitchEntity):
#     def __init__(
#         self,
#         hass: HomeAssistant,  # pylint: disable=unused-argument
#         config: ConfigEntry
#     ) -> None:
#         self.hass = hass
#         self.config_entry = config
#         self._device_id = config.entry_id
#         self._attr_has_entity_name = True
#         self._attr_name = "Flip horizontally"
#         self._attr_icon = "mdi:flip-horizontal"
#         self._attr_unique_id = self._device_id
#         self._attr_is_on = config.data.get(CONF_HORIZONTAL_FLIP)

#     def turn_on(self, **kwargs) -> None:
#         """Turn the entity on."""
#         self._is_on = True

#     def turn_off(self, **kwargs):
#         """Turn the entity off."""
#         self._is_on = False


class P2PCamSwitch(SwitchEntity, RestoreEntity):
    def __init__(self, id, camera, attr, name_suffix: str):
        self._camera = camera
        self._attr = attr
        self._attr_name = f"{camera.name} {name_suffix}"
        self._state = False
        self._device_id = id
        self._attr_unique_id = f"{self._device_id}_{name_suffix.lower().replace(" ", "_")}"
        self._attr_has_entity_name = True

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_id,
            manufacturer="P2PCam",
            model=DOMAIN,
        )

    async def async_turn_on(self, **kwargs):
        self._state = True
        self._camera._attrs[self._attr] = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._state = False
        self._camera._attrs[self._attr] = False
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Restore previous state on startup."""
        last_state = await self.async_get_last_state()
        if last_state and last_state.state == "on":
            self._state = True
            self._camera._attrs[self._attr] = True


async def async_setup_entry(hass, entry, async_add_entities):
    camera_entity = None
    for entity in hass.data["entity_components"]["camera"].entities:
        if entity.unique_id == entry.entry_id:
            camera_entity = entity
            break

    if not camera_entity:
        return

    async_add_entities([
        P2PCamSwitch(entry.entry_id, camera_entity, ATTR_HORIZONTAL, "Flip Horizontally"),
        P2PCamSwitch(entry.entry_id, camera_entity, ATTR_VERTICAL, "Flip Vertically"),
        P2PCamSwitch(entry.entry_id, camera_entity, ATTR_TIMESTAMP, "Add Timestamp"),
    ])
