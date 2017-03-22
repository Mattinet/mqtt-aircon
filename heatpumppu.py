"""
Demo platform that offers a fake climate device.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import logging
import homeassistant.loader as loader
import homeassistant.components.mqtt as mqtt
from homeassistant.components.climate import (
    ClimateDevice, ATTR_OPERATION_MODE, ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW, ATTR_OPERATION_LIST, ATTR_FAN_MODE,
    ATTR_FAN_LIST, ATTR_SWING_MODE, ATTR_SWING_LIST, PLATFORM_SCHEMA)
from homeassistant.components.mqtt import (
    CONF_STATE_TOPIC, CONF_COMMAND_TOPIC, CONF_QOS)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

DEPENDENCIES = ['mqtt']

_LOGGER = logging.getLogger(__name__)

#mqtt = loader.get_component('mqtt')

CONF_NAME = 'name'
DEFAULT_NAME = 'ILP'
CONF_TOPIC = 'topic'
CONF_MIN_TEMP = 'min_temp'
CONF_MAX_TEMP = 'max_temp'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOPIC): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MAX_TEMP): vol.Coerce(float),
    vol.Optional(CONF_MIN_TEMP): vol.Coerce(float),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Demo climate devices."""
    name = config.get(CONF_NAME)
    topic = config.get(CONF_TOPIC)
    min_temp = config.get(CONF_MIN_TEMP)
    max_temp = config.get(CONF_MAX_TEMP)
    add_devices([
        ILPClimate(hass, name, min_temp, max_temp, 21, TEMP_CELSIUS, False, False, "Auto",
                   "Off", "Heat", None, None, topic),
    ])

class ILPClimate(ClimateDevice):
    """Representation of a demo climate device."""

    def __init__(self, hass, name, min_temp, max_temp,target_temperature, 
                 unit_of_measurement, sensor, away, current_fan_mode,
                 current_swing_mode, current_operation, 
                 target_temp_high, target_temp_low, topic):
        """Initialize the climate device."""
        self._hass = hass
        self._name = name
        self._min_temp = min_temp
        self._max_temp = max_temp
        self._target_temperature = target_temperature
        self._unit_of_measurement = unit_of_measurement
        self._sensor_mode = sensor
        self._away_mode = away
#        self._current_temperature = current_temperature
        self._current_fan_mode = current_fan_mode
        self._current_operation = current_operation
        self._current_swing_mode = current_swing_mode
        self._fan_list = ["Auto", "High", "Med", "Low", "Quiet"]
        self._operation_list = ["Heat", "Cool", "Dry", "Fan", "Auto"]
        self._swing_list = ["Off", "Vertical", "Horizontal", "Both"]
        self._target_temperature_high = target_temp_high
        self._target_temperature_low = target_temp_low
        self._topic = topic

    @property
    def should_poll(self):
        """Polling not needed for a demo climate device."""
        return False

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        # pylint: disable=no-member
        if self._min_temp:
            return self._min_temp
        else:
            # get default temp from super class
            return ClimateDevice.min_temp.fget(self)

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        # pylint: disable=no-member
        if self._max_temp:
            return self._max_temp
        else:
            # Get default temp from super class
            return ClimateDevice.max_temp.fget(self)

#    @property
#    def current_temperature(self):
#        """Return the current temperature."""
#        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self._target_temperature_high

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self._target_temperature_low

#    @property
#    def current_humidity(self):
#        """Return the current humidity."""
#        return self._current_humidity

#    @property
#    def target_humidity(self):
#        """Return the humidity we try to reach."""
#        return self._target_humidity

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self._operation_list

    @property
    def is_sensor_mode_on(self):
        """Return if sensor mode is on."""
        return self._sensor_mode

    @property
    def is_away_mode_on(self):
        """Return if away mode is on."""
        return self._away_mode

#    @property
#    def is_aux_heat_on(self):
#        """Return true if away mode is on."""
#        return self._aux

    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_list(self):
        """List of available fan modes."""
        return self._fan_list

    @property
    def topic(self):
        """return the mqtt topic"""
        return self._topic

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None and \
           kwargs.get(ATTR_TARGET_TEMP_LOW) is not None:
            self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            self._target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        mqtt.publish(self._hass, self._topic+"/temp", payload=self._target_temperature, qos=0, retain=True)
        self.update_ha_state()

#    def set_humidity(self, humidity):
#        """Set new target temperature."""
#        self._target_humidity = humidity
#        self.update_ha_state()

    def set_sensor_mode(self, sensor_mode):
        """Set new sensor mode."""
        self._current_sensor_mode = sensor_mode
        mqtt.publish(self._hass, self._topic+"/sensor", payload=sensor_mode, qos=0, retain=True)
        self.update_ha_state()

    def set_swing_mode(self, swing_mode):
        """Set new swing mode."""
        self._current_swing_mode = swing_mode
        mqtt.publish(self._hass, self._topic+"/swing_mode", payload=swing_mode, qos=0, retain=True)
        self.update_ha_state()

    def set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        self._current_fan_mode = fan_mode
        mqtt.publish(self._hass, self._topic+"/fan_mode", payload=fan_mode, qos=0, retain=True)
        self.update_ha_state()

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        self._current_operation = operation_mode
        mqtt.publish(self._hass, self._topic+"/master_mode", payload=operation_mode, qos=0, retain=True)
        self.update_ha_state()

    @property
    def current_swing_mode(self):
        """Return the swing setting."""
        return self._current_swing_mode

    @property
    def swing_list(self):
        """List of available swing modes."""
        return self._swing_list

    @property
    def sensor_mode_on(self):
        """Turn sensor mode on."""
        self._sensor_mode = True
        self.update_ha_state()

    @property
    def sensor_mode_off(self):
        """Turn sensor mode off."""
        self._sensor_mode = False
        self.update_ha_state()

    def turn_away_mode_on(self):
        """Turn away mode on."""
        self._away_mode = True
        self.update_ha_state()

    def turn_away_mode_off(self):
        """Turn away mode off."""
        self._away_mode = False
        self.update_ha_state()

#    def turn_aux_heat_on(self):
#        """Turn away auxillary heater on."""
#        self._aux = True
#        self.update_ha_state()

#    def turn_aux_heat_off(self):
#        """Turn auxillary heater off."""
#        self._aux = False
#        self.update_ha_state()
