"""Platform for the Airbnk AC."""
import asyncio
import datetime
import logging
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import SERVICE_RELOAD
from .const import DOMAIN, AIRBNK_API, AIRBNK_DEVICES

from .airbnk_api import AirbnkApi

_LOGGER = logging.getLogger(__name__)

ENTRY_IS_SETUP = "airbnk_entry_is_setup"

PARALLEL_UPDATES = 0

SERVICE_FORCE_UPDATE = "force_update"
SERVICE_PULL_DEVICES = "pull_devices"

SIGNAL_DELETE_ENTITY = "airbnk_delete"
SIGNAL_UPDATE_ENTITY = "airbnk_update"

TOKENSET_FILE = "tokenset.json"

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=15)

COMPONENT_TYPES = ["lock", "sensor"]


CONFIG_SCHEMA = vol.Schema(vol.All({DOMAIN: vol.Schema({})}), extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Setup the Airbnk component."""

    async def _handle_reload(service):
        """Handle reload service call."""
        _LOGGER.debug("Service %s.reload called: reloading integration", DOMAIN)

        current_entries = hass.config_entries.async_entries(DOMAIN)

        reload_tasks = [
            hass.config_entries.async_reload(entry.entry_id)
            for entry in current_entries
        ]

        await asyncio.gather(*reload_tasks)
        _LOGGER.debug("RELOAD DONE")

    hass.helpers.service.async_register_admin_service(
        DOMAIN,
        SERVICE_RELOAD,
        _handle_reload,
    )

    if DOMAIN not in config:
        return True

    conf = config.get(DOMAIN)
    if conf is not None:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Establish connection with Airbnk."""

    airbnk_api = AirbnkApi(hass, entry)

    devices = await airbnk_api.getCloudDevices()
    hass.data[DOMAIN] = {AIRBNK_API: airbnk_api, AIRBNK_DEVICES: devices}
    
    await hass.config_entries.async_forward_entry_setups(entry, COMPONENT_TYPES)
    return True
    

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await asyncio.wait(
        [
            hass.config_entries.async_forward_entry_unload(config_entry, component)
            for component in COMPONENT_TYPES
        ]
    )
    hass.data[DOMAIN].pop(config_entry.entry_id)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return True


async def airbnk_api_setup(hass, host, key, uuid, password):
    """Create a Airbnk instance only once."""
    return
