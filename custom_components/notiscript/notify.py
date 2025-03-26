"""Notification platform that calls scripts.

This notification platform allows calling scripts with transformed data structures.
It provides two main transformation mechanisms:

1. Script Selection (script_suffix):
   - Priority 1: From notification data
   - Priority 2: From configuration
   - Priority 3: From notifier name

2. Data Transformation (script_fields):
   - Priority 1: From notification data
   - Priority 2: From configuration

When script_fields is present:
   - The values from script_fields are passed directly to the script
   - Original notification fields (message, title, etc.) are moved to data.notifier_fields
   - All other data from the notification is preserved in data

Example:
    Configuration:
        notify:
          - platform: notiscript
            name: my_notifier
            script_suffix: my_script
            script_fields:
              message: "msg"
              title: "heading"

    Notification call:
        service: notify.my_notifier
        data:
          message: "Hello"
          title: "Test"
          data:
            script_fields:
              message: "msg"
              title: "heading"
            custom_field: "value"

    Result sent to script:
        {
            "message": "msg",
            "title": "heading",
            "data": {
                "custom_field": "value",
                "notifier_fields": {
                    "message": "Hello",
                    "title": "Test"
                }
            }
        }
"""
import logging
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_SCRIPT_SUFFIX = "script_suffix"
CONF_SCRIPT_FIELDS = "script_fields"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_SCRIPT_SUFFIX): cv.string,
        vol.Optional(CONF_SCRIPT_FIELDS): vol.Schema({str: str}),  # Object with string keys and values
        vol.Required("name"): cv.string,  # wichtig für Zugriff auf den Namen als Fallback
    }
)


async def async_get_service(hass, config, discovery_info=None):
    """Get the notiscript notification service.
    
    This is a required function signature from Home Assistant.
    It is called by Home Assistant to initialize the notification service.
    
    Args:
        hass: The Home Assistant instance
        config: Configuration dictionary containing:
            - name: Name of the notifier
            - script_suffix: Optional script name to call
            - script_fields: Optional fields to pass to script
        discovery_info: Optional discovery information
        
    Returns:
        An instance of NotiScriptNotificationService
    """
    config_script_suffix = config.get(CONF_SCRIPT_SUFFIX)
    config_script_fields = config.get(CONF_SCRIPT_FIELDS, {})
    notifier_name = config["name"]
    _LOGGER.debug(f"[notiscript] Setting up notifier '{notifier_name}' with config script: {config_script_suffix}, script_fields: {config_script_fields}")
    return NotiScriptNotificationService(hass, notifier_name, config_script_suffix, config_script_fields)


class NotiScriptNotificationService(BaseNotificationService):
    """Implementation of the notiscript notification service.
    
    This service inherits from BaseNotificationService and provides a flexible way
    to transform notification data and call scripts. It supports two main features:
    
    1. Dynamic script selection through script_suffix
    2. Data transformation through script_fields
    
    The service can be configured in configuration.yaml and supports runtime
    overrides through notification data.
    """

    def __init__(self, hass, notifier_name, config_script_suffix, config_script_fields):
        """Initialize the notification service.
        
        Args:
            hass: The Home Assistant instance
            notifier_name: Name of the notifier
            config_script_suffix: Script name from configuration
            config_script_fields: Fields to pass to script from configuration
        """
        self.hass = hass
        self.config_script_suffix = config_script_suffix
        self.config_script_fields = config_script_fields
        self.notifier_name = notifier_name

    async def async_send_message(self, message="", **kwargs):
        """Send a notification message.
        
        This is a required method signature from Home Assistant.
        It is called by Home Assistant when a notification should be sent.
        
        This method transforms the notification data according to script_fields
        and calls the appropriate script with the transformed data.
        
        Args:
            message: The notification message (required by Home Assistant)
            **kwargs: Additional notification data including:
                - title: Optional notification title
                - data: Optional dictionary of additional data
                - script_suffix: Optional override for script name
                - script_fields: Optional override for fields to pass to script
        """
        # Define all standard notification fields with default values
        standard_fields = {
            ATTR_MESSAGE: message,
            ATTR_TITLE: kwargs.get(ATTR_TITLE),
            ATTR_TARGET: kwargs.get(ATTR_TARGET),
            ATTR_DATA: kwargs.get(ATTR_DATA) or {},  # Ensure data is always a dictionary
        }

        # Handling script_suffix
        ########################

        # Prio 1: script_suffix from data from notifier call
        script_suffix = standard_fields[ATTR_DATA].get(CONF_SCRIPT_SUFFIX)

        # Prio 2: script_suffix from configuration of notifier in configuration.yaml
        if not script_suffix and self.config_script_suffix:
            script_suffix = self.config_script_suffix

        # Prio 3: script_suffix is the notifier_name in the configuration.yaml 
        if not script_suffix:
            script_suffix = self.notifier_name

        # Handling script_fields
        ########################

        # Prio 1: script_fields from data from notifier call
        script_fields = standard_fields[ATTR_DATA].get(CONF_SCRIPT_FIELDS, {})

        # Prio 2: script_fields from configuration of notifier in configuration.yaml
        if not script_fields and self.config_script_fields:
            script_fields = self.config_script_fields

        # Remove control parameters from data
        # These are special parameters that control the behavior of the notifier
        # and should not be passed to the script
        control_parameters = {CONF_SCRIPT_SUFFIX, CONF_SCRIPT_FIELDS}
        for param in control_parameters:
            if param in standard_fields[ATTR_DATA]:
                del standard_fields[ATTR_DATA][param]

        # If script_fields is present, move specified fields to data.notifier_fields
        if script_fields:
            notifier_fields = {}
            
            # Add all standard fields that have values
            for field, value in standard_fields.items():
                if value is not None:
                    notifier_fields[field] = value
            
            # Add any additional fields from kwargs that aren't control parameters
            control_parameters = {CONF_SCRIPT_SUFFIX, CONF_SCRIPT_FIELDS}
            for key, value in kwargs.items():
                if key not in control_parameters:
                    notifier_fields[key] = value
            
            # Create service_data with script_fields values and preserve all original data
            service_data = script_fields.copy()
            service_data["data"] = standard_fields[ATTR_DATA].copy()  # Keep all original data
            service_data["data"]["notifier_fields"] = notifier_fields  # Add notifier_fields to it
        else:
            # When no script_fields, include all fields directly
            # Create service_data with all standard fields that have values
            service_data = {}
            for field, value in standard_fields.items():
                if value is not None:
                    service_data[field] = value
            
            # Add any additional fields from kwargs that aren't control parameters
            control_parameters = {CONF_SCRIPT_SUFFIX, CONF_SCRIPT_FIELDS}
            for key, value in kwargs.items():
                if key not in control_parameters:
                    service_data[key] = value

        _LOGGER.debug(f"[notiscript] Calling script: script.{script_suffix} with data: {service_data}")

        try:
            await self.hass.services.async_call(
                domain="script",
                service=script_suffix,
                service_data=service_data,
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error(f"[notiscript] Failed to call script.{script_suffix}: {e}")
