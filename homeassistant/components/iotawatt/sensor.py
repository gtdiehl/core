"""Support for IoTaWatt Energy monitor."""
from datetime import timedelta
import logging

from homeassistant.const import DEVICE_CLASS_ENERGY
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

ICON = "mdi:flash"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    iotawatt = hass.data[DOMAIN][config_entry.entry_id]

    async def async_update_data():
        await iotawatt.update()
        return iotawatt.getSensors()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_refresh()

    async_add_devices(
        IOSensor(coordinator, ent)
        for idx, ent in enumerate(coordinator.data["sensors"])
    )


class IOSensor(CoordinatorEntity):
    """Implementation of the IoTaWatt sensors."""

    device_class = DEVICE_CLASS_ENERGY

    def __init__(self, coordinator, ent):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._ent = ent
        self._io_type = self._coordinator.data["sensors"][self._ent].getType()

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        if self._io_type == "Input":
            channel = self._coordinator.data["sensors"][self._ent].getChannel()
        else:
            channel = "N/A"

        return {"Type": self._io_type, "Channel": channel}

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._coordinator.data["sensors"][self._ent].getUnit()

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._coordinator.data["sensors"][self._ent].getValue()

    @property
    def name(self):
        """Return the name of the sensor."""
        name = (
            "IoTaWatt "
            + str(self._io_type)
            + " "
            + str(self._coordinator.data["sensors"][self._ent].getName())
        )
        return name
