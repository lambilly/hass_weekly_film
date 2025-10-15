"""Config flow for Weekly Film integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_API_KEY, CONF_SCROLL_INTERVAL, DEFAULT_SCROLL_INTERVAL

class WeeklyFilmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Weekly Film."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="每周电影", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_SCROLL_INTERVAL, default=DEFAULT_SCROLL_INTERVAL): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                "api_url": "https://qqlykm.cn/"
            },
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return WeeklyFilmOptionsFlow(config_entry)

class WeeklyFilmOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Weekly Film."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCROLL_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCROLL_INTERVAL, DEFAULT_SCROLL_INTERVAL
                    ),
                ): int,
            }),
        )