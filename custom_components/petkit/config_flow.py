"""Adds config flow for Petkit Smart Devices."""

from __future__ import annotations

from pypetkitapi import PetkitAuthenticationError, PetKitClient, PypetkitError
import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import COUNTRY_CODES, DOMAIN, LOGGER, REGION, TIMEZONE, TIMEZONES


class PetkitFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Petkit Smart Devices."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        country_from_ha = COUNTRY_CODES.get(self.hass.config.country, "Unknown")
        tz_from_ha = self.hass.config.time_zone
        LOGGER.debug(
            f"Country code from HA : {self.hass.config.country} Detected country : {country_from_ha} Default timezone: {tz_from_ha}"
        )

        if user_input is not None:
            # Check if the account already exists
            existing_entries = self._async_current_entries()
            for entry in existing_entries:
                if entry.data.get(CONF_USERNAME) == user_input[CONF_USERNAME]:
                    _errors["base"] = "account_exists"
                    break
            else:
                try:
                    await self._test_credentials(
                        username=user_input[CONF_USERNAME],
                        password=user_input[CONF_PASSWORD],
                        region=user_input.get(REGION, country_from_ha),
                        timezone=user_input.get(TIMEZONE, tz_from_ha),
                    )
                except PetkitAuthenticationError as exception:
                    LOGGER.error(exception)
                    _errors["base"] = str(exception)
                except PypetkitError as exception:
                    LOGGER.error(exception)
                    _errors["base"] = "error"
                else:
                    return self.async_create_entry(
                        title=user_input[CONF_USERNAME],
                        data=user_input,
                    )

        data_schema = {
            vol.Required(
                CONF_USERNAME,
                default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        }

        if _errors:
            data_schema.update(
                {
                    vol.Required(
                        REGION, default=country_from_ha
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=sorted(COUNTRY_CODES.values())
                        ),
                    ),
                    vol.Required(TIMEZONE, default=tz_from_ha): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=TIMEZONES),
                    ),
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=_errors,
        )

    async def _test_credentials(
        self, username: str, password: str, region: str, timezone: str
    ) -> None:
        """Validate credentials."""
        client = PetKitClient(
            username=username,
            password=password,
            region=region,
            timezone=timezone,
            session=async_get_clientsession(self.hass),
        )
        LOGGER.debug(f"Testing credentials for {username}")
        await client.login()
