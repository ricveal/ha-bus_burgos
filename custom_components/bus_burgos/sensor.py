"""Support Burgos Bus service."""
from __future__ import annotations

from contextlib import suppress

import bus_burgos
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

CONF_STOP_ID = "stopid"
CONF_ROUTE = "route"

DEFAULT_NAME = "Next bus"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STOP_ID): cv.string,
        vol.Required(CONF_ROUTE): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the BusBurgos public transport sensor."""
    name = config[CONF_NAME]
    stop = config[CONF_STOP_ID]
    route = config[CONF_ROUTE]
    client = aiohttp_client.async_get_clientsession(hass)
    data = BusBurgos(client, stop, route)
    add_entities([BusBurgosSensor(data, name)], True)


class BusBurgosSensor(SensorEntity):
    """The class for handling the data."""

    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, data, name):
        """Initialize the sensor."""
        self.data = data
        self._attr_name = name

    def update(self) -> None:
        """Get the latest data from the webservice."""
        self.data.update()
        with suppress(TypeError):
            self._attr_native_value = self.data.info.seconds


class BusBurgos:
    """The class for handling the data retrieval."""

    def __init__(self, client, stop, route):
        """Initialize the data object."""
        self.client = client
        self.stop = stop
        self.route = route
        self.info = None

    def update(self):
        """Retrieve the information from API."""
        bus_stop = bus_burgos.get_bus_stop(self.client, self.stop)
        self.info = bus_stop.get_next_bus(self.route)
