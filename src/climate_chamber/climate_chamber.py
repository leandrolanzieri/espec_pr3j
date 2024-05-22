#!/usr/bin/python3
import logging
import re
import time

import pyvisa

from .data_classes import (
    HeatersStatus,
    HumidityStatus,
    OperationMode,
    TemperatureStatus,
    TestAreaState,
)
from .exceptions import SettingError

_LOGGER = logging.getLogger(__name__)


class ClimateChamber:
    """
    Implements the basic operation of the climate chamber.

    Args:
        `ip_address (str | None)`: IP address of the climate chamber. Default is None.
            If None, the resource_path must be provided. Can't be used with
            resource_path.
        `temperature_accurary (float)`: The accuracy considered when setting the
            temperature. Default is 0.2.
        `humidity_accuracy (float)`: The accuracy considered when setting the humidity.
            Default is 1.0.
        `resource_path (str | None)`: The resource path of the climate chamber. Default
            is None. If None, the ip_address must be provided. Can't be used with
            ip_address.
        `resource_namager (pyvisa.ResourceManager | None)`: An optional PyVISA resource
            manager. If None, the default one is used
    """

    MONITOR_COMMAND_DELAY = 0.2
    """Delay in seconds when sending a command to the climate chamber
       (program-related delay is 0.3)"""

    SETTING_COMMAND_DELAY = 0.5
    """Delay in seconds when sending a setting command to the climate chamber
       (program-related delay is 1)"""

    TCP_PORT = 57732
    """The TCP port of the climate chamber"""

    def __init__(
        self,
        ip_address: str | None = None,
        temperature_accurary=0.2,
        humidity_accuracy=1.0,
        resource_path: str | None = None,
        resource_manager: pyvisa.ResourceManager = None,
    ):
        assert (ip_address is None) or (resource_path is None)
        assert (ip_address is not None) or (resource_path is not None)

        self.ip_address = ip_address
        """The IP address of the climate chamber"""

        self.temperature_accuracy = temperature_accurary
        """The accuracy considered when setting the temperature"""

        self.humidity_accuracy = humidity_accuracy
        """The accuracy considered when setting the humidity"""

        # we try to connect to the climate chamber just to see if there is an error
        self._resource_manager = resource_manager or pyvisa.ResourceManager()

        if resource_path is None:
            resource_path = f"TCPIP0::{self.ip_address}"  # noqa E231
            resource_path += f"::{self.TCP_PORT}::SOCKET"  # noqa E231

        self.resource_path = resource_path
        """Resource path of the climate chamber"""

        self._chamber = self._resource_manager.open_resource(self.resource_path)
        _LOGGER.debug(f"Connected to the climate chamber at {self.resource_path}")

        self._chamber.write_termination = "\r\n"
        self._chamber.read_termination = "\r\n"
        self._chamber.timeout = 5000

    def _target_temperature_reached(self) -> bool:
        """
        Checks if the current temperature is within the target temperature range.
        """
        temperature_status = self.get_temperature_status()
        current = temperature_status.current_temperature
        target = temperature_status.target_temperature

        _LOGGER.debug(
            f"Current temperature: {current}°C, Target temperature: {target} +-"
            f"{self.temperature_accuracy}°C"
        )
        return (
            (target - self.temperature_accuracy)
            <= current
            <= (target + self.temperature_accuracy)
        )

    def _target_humidity_reached(self) -> bool:
        """
        Checks if the current humidity is within the target humidity range.
        """
        humidity_status = self.get_humidity_status()
        current = humidity_status.current_humidity
        target = humidity_status.target_humidity

        _LOGGER.debug(
            f"Current humidity: {current}%, Target humidity: {target} +-"
            f"{self.humidity_accuracy}%"
        )
        return (
            (target - self.humidity_accuracy)
            <= current
            <= (target + self.humidity_accuracy)
        )

    def get_temperature_status(self) -> TemperatureStatus:
        """
        Gets the temperature status of the climate chamber. This includes the current
        temperature, set temperature, upper limit, and lower limit.
        """
        # send the request to the chamber
        response = self._chamber.query("TEMP?", delay=self.MONITOR_COMMAND_DELAY)

        # convert into float numbers
        # data format: [current temp, set temp, upper limit, lower limit]
        temperature = [float(i) for i in response.split(sep=",")]

        temperature_status = TemperatureStatus(
            current_temperature=temperature[0],
            target_temperature=temperature[1],
            upper_limit=temperature[2],
            lower_limit=temperature[3],
        )
        return temperature_status

    def get_humidity_status(self) -> HumidityStatus:
        """
        Gets the humidity status of the climate chamber. This includes the current
        humidity, set humidity, upper limit, and lower limit.
        """
        # send the request to the chamber
        response = self._chamber.query("HUMI?", delay=self.MONITOR_COMMAND_DELAY)

        # convert into float numbers
        # data format: [current hum, set hum, upper limit, lower limit]
        humidity = [float(i) for i in response.split(sep=",")]

        humidity_status = HumidityStatus(
            current_humidity=humidity[0],
            target_humidity=humidity[1],
            upper_limit=humidity[2],
            lower_limit=humidity[3],
        )
        return humidity_status

    def set_target_temperature(self, temperature: float):
        """
        Sets the target temperature of the climate chamber.

        Args:
            `temperature`: The target temperature to set in Celsius.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                                          target temperature.
        """
        # sets the temp of the chamber, temperature
        _LOGGER.debug(f"Setting target temperature to {temperature}°C")
        response = self._chamber.query(
            f"TEMP, S{str(temperature)}", delay=self.SETTING_COMMAND_DELAY
        )

        # verify the response
        response_pattern = re.compile(r"OK: TEMP, S\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the target temperature")
            raise SettingError("Failed to set the target temperature")

    def set_target_humidity(self, humidity: float):
        """
        Sets the target humidity of the climate chamber.

        Args:
            `humidity`: The target humidity to set in percentage.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                                          target humidity.
        """
        # sets the humidity of the chamber, (float) humidity
        _LOGGER.debug(f"Setting target humidity to {humidity}%")
        response = self._chamber.query(
            "HUMI, S" + str(humidity), delay=self.SETTING_COMMAND_DELAY
        )

        # verify the response
        response_pattern = re.compile(r"OK: HUMI, S\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the target humidity")
            raise SettingError("Failed to set the target humidity")

    def close(self):
        """
        Closes the connection to the climate chamber.
        """
        _LOGGER.debug("Closing the connection to the climate chamber")
        self._chamber.close()

    def get_test_area_state(self) -> TestAreaState:
        """
        Get the chamber test area state.
        """
        response = self._chamber.query("MON?", delay=self.MONITOR_COMMAND_DELAY)
        state = response.split(sep=",")

        # output data format: [temp, humid, op-state, num. of alarms]
        test_area_state = TestAreaState(
            current_temperature=float(state[0]),
            current_humidity=float(state[1]),
            operation_state=OperationMode.from_str(state[2]),
            number_of_alarms=int(state[3]),
        )
        return test_area_state

    def set_temperature_limits(self, upper_limit: float, lower_limit: float):
        """
        Sets the upper and lower temperature limits for the chamber.

        Args:
            `upper_limit`: The temperature upper limit in Celsius.
            `lower_limit`: The temperature lower limit in Celsius.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                                          temperature limits.
        """
        response = self._chamber.query(f"TEMP, H{upper_limit: 0.1f}")
        response_pattern = re.compile(r"OK: TEMP, H\d+")
        if not response_pattern.match(response):
            raise SettingError("Failed to set the upper temperature limit")

        response = self._chamber.query(f"TEMP, L{lower_limit: 0.1f}")
        response_pattern = re.compile(r"OK: TEMP, L\d+")
        if not response_pattern.match(response):
            raise SettingError("Failed to set the lower temperature limit")

    def set_humidity_limits(self, upper_limit: float, lower_limit: float):
        """
        Sets the upper and lower humidity limits for the chamber

        Args:
            `upper_limit`: The humidity upper limit.
            `lower_limit`: The humidity lower limit.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                                          humidity limits.
        """
        _LOGGER.debug(f"Setting humidity limits to {upper_limit}% and {lower_limit}%")
        response = self._chamber.query("HUMI, H" + str(upper_limit))
        response_pattern = re.compile(r"OK: HUMI, H\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the upper humidity limit")
            raise SettingError("Failed to set the upper humidity limit")

        _LOGGER.debug(f"Setting humidity limits to {upper_limit}% and {lower_limit}%")
        response = self._chamber.query("HUMI, L" + str(lower_limit))
        response_pattern = re.compile(r"OK: HUMI, L\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the lower humidity limit")
            raise SettingError("Failed to set the lower humidity limit")

    def get_mode(self) -> OperationMode:
        """
        Gets the operation mode of the climate chamber.
        """
        response = self._chamber.query("MODE?", delay=self.MONITOR_COMMAND_DELAY)
        return OperationMode.from_str(response)

    def set_mode(self, mode: OperationMode):
        """
        Sets the operation mode of the climate chamber.

        Args:
            `mode`: The operation mode to set.
        """
        # sets the mode of the chamber:
        _LOGGER.debug(f"Setting operation mode to {mode}")
        response = self._chamber.query(
            f"MODE, {mode}", delay=self.SETTING_COMMAND_DELAY
        )
        response_pattern = re.compile(r"OK: MODE, \w+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the operation mode")
            raise SettingError("Failed to set the operation mode")

        return response

    def set_constant_condition(
        self, temperature: float, humidity: float, stable_time=60
    ):
        """
        Sets the climate chamber to a constant temperature and humidity condition and
        waits until the setpoints are reached and stable.

        Args:
            `temperature`: The temperature to set in Celsius.
            `humidity`: The humidity to set in percentage.
            `stable_time`: The time in seconds to wait until the setpoints are stable.
                           Default is 60.
        """
        _LOGGER.debug(f"Setting constant condition {temperature}°C, {humidity}%")

        self.set_target_temperature(temperature)
        self.set_target_humidity(humidity)
        self.set_mode(OperationMode.CONSTANT)

        start_time = time.time()

        _LOGGER.debug("Waiting for the setpoints to be reached")

        while True:
            stable = (
                self._target_temperature_reached() and self._target_humidity_reached()
            )
            if not stable:
                _LOGGER.debug("Setpoints not reached yet")
                start_time = time.time()

            if time.time() - start_time >= stable_time:
                _LOGGER.debug("Setpoints reached and stable")
                break

            time.sleep(1)

    def get_heater_percentage(self) -> HeatersStatus:
        """
        Gets the output of the heaters
        """
        response = self._chamber.query("%?", delay=self.MONITOR_COMMAND_DELAY)
        response = response.split(sep=",")

        heaters = HeatersStatus(
            temperature_heater=float(response[1]), humidity_heater=float(response[2])
        )

        return heaters

    def __del__(self):
        self.close()
