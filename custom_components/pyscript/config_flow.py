"""Config flow for pyscript."""
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_ALL_KEYS, CONF_ALLOW_ALL_IMPORTS, DOMAIN

PYSCRIPT_SCHEMA = vol.Schema(
    {vol.Optional(CONF_ALLOW_ALL_IMPORTS, default=False): bool}, extra=vol.ALLOW_EXTRA,
)


class PyscriptConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a pyscript config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input: Dict[str, Any] = None) -> None:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            if len(self.hass.config_entries.async_entries(DOMAIN)) > 0:
                return self.async_abort(reason="single_instance_allowed")

            await self.async_set_unique_id(DOMAIN)
            return self.async_create_entry(title=DOMAIN, data=user_input)

        return self.async_show_form(step_id="user", data_schema=PYSCRIPT_SCHEMA)

    async def async_step_import(self, import_config: Dict[str, Any] = None) -> None:
        """Import a config entry from configuration.yaml."""
        # Check if import config entry matches any existing config entries
        # so we can update it if necessary
        entries = self.hass.config_entries.async_entries(DOMAIN)
        if entries:
            entry = entries[0]
            updated_data = entry.data.copy()

            # Update key if it's value has been changed
            for key in CONF_ALL_KEYS:
                if entry.data.get(key) != import_config.get(key):
                    if import_config.get(key) is not None:
                        updated_data[key] = import_config[key]
                    else:
                        updated_data.pop(key)

            # Update and reload entry if data needs to be updated
            if updated_data != entry.data:
                self.hass.config_entries.async_update_entry(entry=entry, data=updated_data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="updated_entry")

            return self.async_abort(reason="already_configured_service")

        return await self.async_step_user(user_input=import_config)
