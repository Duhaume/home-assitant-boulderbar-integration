from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from .const import DOMAIN, ROOM_NAMES_TO_IDS, ROOMS_MAPPING
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

API_URL_TEMPLATE = "https://boulderbar.net/wp-json/boulderbar/v1/capacity?locations={locations}"

async def fetch_capacity_data(locations):
    url = API_URL_TEMPLATE.format(locations=",".join(locations))
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("data", [])

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    conf = hass.data[DOMAIN]["config"]
    location_names = conf["locations"]
    location_ids = [ROOM_NAMES_TO_IDS[name] for name in location_names]

    data = await fetch_capacity_data(location_ids)
    sensors = [BoulderBarSensor(loc["title"], loc["capacity"]) for loc in data]
    async_add_entities(sensors, True)

class BoulderBarSensor(SensorEntity):
    def __init__(self, title, initial_capacity):
        self._location_title = title
        self._capacity = initial_capacity
        self._attr_name = f"BoulderBar {title}"
        self._attr_unique_id = f"boulderbar_{title}"
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def state(self):
        return self._capacity

    async def async_update(self):
        all_ids = list(ROOMS_MAPPING.keys())
        data = await fetch_capacity_data(all_ids)
        for location in data:
            if location["title"] == self._location_title:
                self._capacity = location["capacity"]