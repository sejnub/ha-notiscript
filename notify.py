"""Notification platform that calls scripts."""
import logging
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_SCRIPT = "script"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_SCRIPT): cv.string,
        vol.Required("name"): cv.string,  # wichtig für Zugriff auf den Namen als Fallback
    }
)


async def async_get_service(hass, config, discovery_info=None):
    """Get the notiscript notification service."""
    config_script_id = config.get(CONF_SCRIPT)
    notifier_name = config["name"]
    _LOGGER.debug(f"[notiscript] Setting up notifier '{notifier_name}' with config script: {config_script_id}")
    return NotiScriptNotificationService(hass, notifier_name, config_script_id)


class NotiScriptNotificationService(BaseNotificationService):
    """Implementation of the notiscript notification service."""

    def __init__(self, hass, notifier_name, config_script_id):
        self.hass = hass
        self.config_script_id = config_script_id
        self.notifier_name = notifier_name

    async def async_send_message(self, message="", **kwargs):
        title = kwargs.get(ATTR_TITLE)
        data = kwargs.get(ATTR_DATA) or {}

        # Priorität 1: script_id aus data
        script_id = data.get("script_id")

        # Priorität 2: script aus Konfiguration
        if not script_id and self.config_script_id:
            script_id = self.config_script_id

        # Priorität 3: Name des Notifiers
        if not script_id:
            script_id = self.notifier_name

        service_data = {
            "message": message,
            "title": title,
            "data": data,
        }

        _LOGGER.debug(f"[notiscript] Calling script: script.{script_id} with data: {service_data}")

        try:
            await self.hass.services.async_call(
                domain="script",
                service=script_id,
                service_data=service_data,
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error(f"[notiscript] Failed to call script.{script_id}: {e}")
