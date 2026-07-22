"""Config flow for the P2PCam integration"""


from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow, ConfigEntry
from homeassistant.const import CONF_NAME
from typing import Any
import copy
from collections.abc import Mapping
import voluptuous as vol
import logging
import p2pcam
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


def add_suggested_values_to_schema(
    data_schema: vol.Schema,
    suggested_values: Mapping[str, Any]
) -> vol.Schema:
    """Make a copy of the schema, populated with suggested values"""

    # For each schema marker matching items in `suggested_values`,
    # the `suggested_value` will be set. The existing `suggested_value` will
    # be left untouched if there is no matching item.
    schema = {}
    for key, val in data_schema.schema.items():
        new_key = key
        if key in suggested_values and isinstance(key, vol.Marker):
            # Copy the marker to not modify the flow schema
            new_key = copy.copy(key)
            new_key.description = {"suggested_value": suggested_values[key]}
        schema[new_key] = val

    return vol.Schema(schema)


class P2PCamOptionsFlow(OptionsFlow):
    # Initialize an empty dict to store user inputs
    _user_inputs: dict = {}
    # Variable for storing the current config
    config_entry: ConfigEntry = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        # The user inputs are set to the data from the current config entry
        self.config_entry = config_entry
        self._user_inputs = config_entry.data.copy()

    async def async_end(self) -> ConfigFlowResult:
        """Finalization of the config entry creation"""

        # Updating the entry data
        self.hass.config_entries.async_update_entry(
            self.config_entry, data=self._user_inputs
        )

        return self.async_create_entry(title=None, data=None)

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the 'init' step of the config flow"""

        # Option data schema
        option_form = vol.Schema({
            vol.Required("camera_ip"): str
        })

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=add_suggested_values_to_schema(
                    data_schema=option_form, suggested_values=self._user_inputs
                ),
            )

        self._user_inputs.update(user_input)
        return await self.async_end()


class P2PCamConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    # Initialize an empty dict to store user inputs
    _user_inputs: dict = {}
    _discovered_devices: dict = {}

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> P2PCamOptionsFlow:
        """Get options flow for this handler"""
        return P2PCamOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the 'user' step of the config flow"""

        if user_input is None:
            scanner = p2pcam.LanScanner()
            devices = await self.hass.async_add_executor_job(scanner.refresh, timeout=10)
            
            self._discovered_devices = {
                dev.ip: f"{dev.device_id} ({dev.ip})" 
                for dev in devices if dev.online
            }

            if not self._discovered_devices:
                return await self.async_step_manual()

            devices_with_manual = self._discovered_devices.copy()
            devices_with_manual["manual"] = "Enter manually"
            
            schema = vol.Schema({
                vol.Required("device"): vol.In(devices_with_manual)
            })
            return self.async_show_form(step_id="user", data_schema=schema)

        if user_input["device"] == "manual":
            return await self.async_step_manual()

        ip = user_input["device"]
        name = self._discovered_devices[ip]
        self._user_inputs = {
            "name": name,
            "camera_ip": ip
        }
        return self.async_create_entry(title=self._user_inputs["name"], data=self._user_inputs)

    async def async_step_manual(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle manual IP entry"""

        user_form = vol.Schema({
            vol.Required("name"): str,
            vol.Required("camera_ip"): str
        })

        if user_input is None:
            return self.async_show_form(step_id="manual", data_schema=user_form)

        self._user_inputs.update(user_input)
        return self.async_create_entry(title=self._user_inputs["name"], data=self._user_inputs)
