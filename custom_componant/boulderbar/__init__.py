import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_LOCATIONS, ROOMS_MAPPING

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_LOCATIONS): vol.All(cv.ensure_list, [vol.In(list(ROOMS_MAPPING.values()))])
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    hass.data.setdefault(DOMAIN, {})["config"] = conf

    # ✅ Chargement correct de la plateforme sensor
    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
