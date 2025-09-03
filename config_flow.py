"""Config flow for the P2PCam integration"""

import logging

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow, ConfigEntry
from .const import DOMAIN, CONF_NAME

import voluptuous as vol

from typing import Any
import copy
from collections.abc import Mapping

_LOGGER = logging.getLogger(__name__)


def add_suggested_values_to_schema(
    data_schema: vol.Schema, suggested_values: Mapping[str, Any]
) -> vol.Schema:
    """Make a copy of the schema, populated with suggested values.

    For each schema marker matching items in `suggested_values`,
    the `suggested_value` will be set. The existing `suggested_value` will
    be left untouched if there is no matching item.
    """
    schema = {}
    for key, val in data_schema.schema.items():
        new_key = key
        if key in suggested_values and isinstance(key, vol.Marker):
            # Copy the marker to not modify the flow schema
            new_key = copy.copy(key)
            new_key.description = {"suggested_value": suggested_values[key]}
        schema[new_key] = val
    _LOGGER.debug("add_suggested_values_to_schema: schema=%s", schema)
    return vol.Schema(schema)


class P2PCamConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    _user_inputs: dict = {}

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get options flow for this handler"""
        return P2PCamOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Gestion de l'étape 'user'. Point d'entrée de notre
        configFlow. Cette méthode est appelée 2 fois :
        1. une première fois sans user_input -> on affiche le formulaire de configuration
        2. une deuxième fois avec les données saisies par l'utilisateur dans user_input -> on sauvegarde les données saisies
        """
        user_form = vol.Schema({
            vol.Required("name"): str,
            vol.Required("host_ip"): str,
            vol.Required("camera_ip"): str
        })

        if user_input is None:
            _LOGGER.debug(
                "config_flow step user (1). 1er appel : pas de user_input -> on affiche le form user_form"
            )
            return self.async_show_form(step_id="user", data_schema=user_form)

        # 2ème appel : il y a des user_input -> on stocke le résultat
        # TODO: utiliser les user_input
        _LOGGER.debug("config_flow step user (2). On a reçu les valeurs: %s", user_input)

        self._user_inputs.update(user_input)

        return self.async_create_entry(title=self._user_inputs["name"], data=self._user_inputs)


class P2PCamOptionsFlow(OptionsFlow):
    """La classe qui implémente le option flow pour notre DOMAIN.
    Elle doit dériver de OptionsFlow"""

    # les données de l'utilisateur
    _user_inputs: dict = {}
    # Pour mémoriser la config en cours
    config_entry: ConfigEntry = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialisation de l'option flow. On a le ConfigEntry existant en entrée"""
        self.config_entry = config_entry
        # On initialise les user_inputs avec les données du configEntry
        self._user_inputs = config_entry.data.copy()

    async def async_end(self):
        """Finalization of the ConfigEntry creation"""
        # _LOGGER.info(
        #     "Recreation de l'entry %s. La nouvelle config est maintenant : %s",
        #     self.config_entry.entry_id,
        #     self._user_inputs,
        # )
        # Modification des data de la configEntry
        # (et non pas ajout d'un objet options dans la configEntry)
        self.hass.config_entries.async_update_entry(
            self.config_entry, data=self._user_inputs
        )
        # On ne fait rien dans l'objet options dans la configEntry
        return self.async_create_entry(title=None, data=None)

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Gestion de l'étape 'init'. Point d'entrée de notre
        optionsFlow. Comme pour le ConfigFlow, cette méthode est appelée 2 fois
        """

        option_form = vol.Schema({
            vol.Required("host_ip"): str,
            vol.Required("camera_ip"): str
        })

        if user_input is None:
            _LOGGER.debug(
                "option_flow step user (1). 1er appel : pas de user_input -> "
                "on affiche le form user_form"
            )
            return self.async_show_form(
                step_id="init",
                # On ajoute les user_inputs comme suggested values au formulaire
                data_schema=add_suggested_values_to_schema(
                    data_schema=option_form, suggested_values=self._user_inputs
                ),
            )

        # 2ème appel : il y a des user_input -> on stocke le résultat
        _LOGGER.debug(
            "option_flow step user (2). On a reçu les valeurs: %s", user_input
        )
        # On mémorise les user_input
        self._user_inputs.update(user_input)

        # On appelle le step de fin pour enregistrer les modifications
        return await self.async_end()
