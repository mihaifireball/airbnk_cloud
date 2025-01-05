"""Support for Airbnk locks, treated as covers."""
import logging

from homeassistant.components.lock import LockEntity

from .const import DOMAIN as AIRBNK_DOMAIN, AIRBNK_API, AIRBNK_DEVICES, CONF_LOCKSTATUS, LOCK_STATE_LOCKED, LOCK_STATE_UNLOCKED

_LOGGER = logging.getLogger(__name__)

LOCK_ICON = "hass:door-closed-lock"
UNLOCK_ICON = "hass:door-closed"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up the platform.

    Can only be called when a user accidentally mentions the platform in their
    config. But even in that case it would have been ignored.
    """


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Airbnk covers based on config_entry."""
    locks = []
    for dev_id, device in hass.data[AIRBNK_DOMAIN][AIRBNK_DEVICES].items():
        lock = AirbnkLock(hass.data[AIRBNK_DOMAIN][AIRBNK_API], device, dev_id)
        locks.append(lock)
    async_add_entities(locks)


class AirbnkLock(LockEntity):
    """Representation of a lock."""

    def __init__(self, api, device, lock_id: str):
        """Initialize the zone."""
        self._api = api
        self._device = device
        self._lock_id = lock_id
        deviceName = self._device["deviceName"]
        self._name = f"{deviceName}"


    @property
    def unique_id(self):
        """Return a unique ID."""
        devID = self._device["sn"]
        return f"{devID}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._api.devices[self._lock_id][CONF_LOCKSTATUS] == LOCK_STATE_LOCKED:
            return LOCK_ICON
        else:
            return UNLOCK_ICON

    @property
    def name(self):
        """Return the name of the lock."""
        return self._name

    @property
    def device_info(self):
        """Return a device description for device registry."""
        devID = self._device["sn"]
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (AIRBNK_DOMAIN, devID)
            },
            "manufacturer": "Airbnk",
            "model": self._device["deviceType"],
            "name": self._device["deviceName"],
            "sw_version": self._device["firmwareVersion"],
        }

#    @property
#    def state(self):
#        status = self._api.devices[self._lock_id][CONF_LOCKSTATUS]
#        return status
        
    @property
    def is_unlocking(self):
        """Return if cover is opening."""
        return False

    @property
    def is_locking(self):
        """Return if cover is closing."""
        return False

    @property
    def is_locked(self):
        """Return if the lock is locked or not."""
        if self._api.devices[self._lock_id][CONF_LOCKSTATUS] == LOCK_STATE_LOCKED:
            return True
        else:
            return False

    async def async_unlock(self, **kwargs):
        """Open the cover."""
        _LOGGER.debug("Launching command to open")
        res = await self._api.operateLock(self._device["sn"], True)
        # raise Exception(res)

    async def async_lock(self, **kwargs):
        """Close cover."""
        _LOGGER.debug("Launching command to close")
        res = await self._api.operateLock(self._device["sn"], False)
        # raise Exception(res)

    async def async_update(self):
        """Retrieve latest state."""
        # _LOGGER.debug("async_update")
