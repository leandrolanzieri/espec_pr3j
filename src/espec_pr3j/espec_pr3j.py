#!/usr/bin/python3
import logging
import re
import time
from typing import Optional

import pyvisa

from .data_classes import (
    HeatersStatus,
    HumidityStatus,
    OperationMode,
    TemperatureStatus,
    TestAreaState,
)
from .exceptions import MonitorError, SettingError

_LOGGER = logging.getLogger(__name__)


class EspecPr3j:
    """
    Implements the basic operation of the environmental chamber.

    Args:
        `hostname (Optional[str])`: Host name of the environmental chamber. Default is
            None. If None, the resource_path must be provided. Can't be used with
            resource_path. It can be an IP address.
        `temperature_accuracy (Optional[float])`: The accuracy considered when setting
            the temperature. Default is 0.5.
        `humidity_accuracy (Optional[float])`: The accuracy considered when setting the
            humidity. Default is 3.0.
        `resource_path (Optional[str])`: The resource path of the environmental chamber.
            If None, the hostname must be provided. Can't be used with hostname. Default
            is None.
        `resource_namager (Optional[pyvisa.ResourceManager])`: An optional PyVISA
            resource manager. If None, the default one is used. Default is None.
        `communication_timeout (Optional[int])`: The communication timeout in
            milliseconds. Default is 5000.
    """

    MONITOR_COMMAND_DELAY = 0.2
    """Delay in seconds when sending a command to the environmental chamber
       (program-related delay is 0.3)"""

    SETTING_COMMAND_DELAY = 0.5
    """Delay in seconds when sending a setting command to the environmental chamber
       (program-related delay is 1)"""

    LINE_TERMINATION = "\r\n"
    """The line termination character used by the environmental chamber"""

    TCP_PORT = 57732
    """The TCP port of the environmental chamber"""

    def __init__(
        self,
        hostname: Optional[str] = None,
        temperature_accuracy: Optional[float] = None,
        humidity_accuracy: Optional[float] = None,
        resource_path: Optional[str] = None,
        resource_manager: Optional[pyvisa.ResourceManager] = None,
        communication_timeout: Optional[int] = None,
    ):
        assert (hostname is None) or (resource_path is None)
        assert (hostname is not None) or (resource_path is not None)

        self.hostname = hostname
        """The IP address of the environmental chamber"""

        self.temperature_accuracy = temperature_accuracy or 0.5
        """The accuracy considered when setting the temperature"""

        self.humidity_accuracy = humidity_accuracy or 3.0
        """The accuracy considered when setting the humidity"""

        # we try to connect to the environmental chamber just to see if there is an
        # error
        self._resource_manager = resource_manager or pyvisa.ResourceManager()

        if resource_path is None:
            resource_path = f"TCPIP0::{self.hostname}"  # noqa E231
            resource_path += f"::{self.TCP_PORT}::SOCKET"  # noqa E231

        self.resource_path = resource_path
        """Resource path of the environmental chamber"""

        self._chamber = self._resource_manager.open_resource(self.resource_path)
        _LOGGER.debug(f"Connected to the environmental chamber at {self.resource_path}")

        self._chamber.write_termination = self.LINE_TERMINATION
        self._chamber.read_termination = self.LINE_TERMINATION
        self._chamber.timeout = communication_timeout or 5000

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
        return abs(current - target) <= self.temperature_accuracy

    def _target_humidity_reached(self) -> bool:
        """
        Checks if the current humidity is within the target humidity range. If the
        humidity control is disabled, it always returns True.
        """
        humidity_status = self.get_humidity_status()
        current = humidity_status.current_humidity
        target = humidity_status.target_humidity

        if target is None:
            _LOGGER.debug("Humidity control is disabled")
            return True

        _LOGGER.debug(
            f"Current humidity: {current}%, Target humidity: {target} +-"
            f"{self.humidity_accuracy}%"
        )
        return abs(current - target) <= self.humidity_accuracy

    def get_temperature_status(self) -> TemperatureStatus:
        """
        Gets the temperature status of the environmental chamber. This includes the
        current temperature, set temperature, upper limit, and lower limit.

        Raises:
            `MonitorError`: If an error occurred when getting the temperature status.
        """
        # send the request to the chamber
        response = self._chamber.query("TEMP?", delay=self.MONITOR_COMMAND_DELAY)

        # data format: [current temp, set temp, upper limit, lower limit]
        pattern = re.compile(
            r"(?P<current>\d+\.\d+)"
            r",(?P<target>\d+\.\d+)"
            r",(?P<upper>\d+\.\d+)"
            r",(?P<lower>\d+\.\d+)"
        )

        match = pattern.match(response)
        if match is None:
            _LOGGER.error("Failed to get the temperature status")
            _LOGGER.debug(f"Response: '{response}'")
            raise MonitorError("Failed to get the temperature status")

        # convert into float numbers
        temperature_status = TemperatureStatus(
            current_temperature=float(match["current"]),
            target_temperature=float(match["target"]),
            upper_limit=float(match["upper"]),
            lower_limit=float(match["lower"]),
        )

        return temperature_status

    def get_humidity_status(self) -> HumidityStatus:
        """
        Gets the humidity status of the environmental chamber. This includes the current
        humidity, set humidity, upper limit, and lower limit.

        Raises:
            `MonitorError`: If an error occurred when getting the humidity status.
        """
        # send the request to the chamber
        response = self._chamber.query("HUMI?", delay=self.MONITOR_COMMAND_DELAY)

        # data format: [current humi, set humi, upper limit, lower limit]
        pattern = re.compile(
            r"(?P<current>\d+)"
            r",(?P<target>OFF|\d+)"
            r",(?P<upper>\d+)"
            r",(?P<lower>\d+)"
        )

        match = pattern.match(response)
        if match is None:
            _LOGGER.error("Failed to get the temperature status")
            _LOGGER.debug(f"Response: '{response}'")
            raise MonitorError("Failed to get the humidity status")

        if match["target"] == "OFF":
            target_humidity = None
        else:
            target_humidity = float(match["target"])

        # convert into float numbers
        humidity_status = HumidityStatus(
            current_humidity=float(match["current"]),
            target_humidity=target_humidity,
            upper_limit=float(match["upper"]),
            lower_limit=float(match["lower"]),
        )

        return humidity_status

    def set_target_temperature(self, temperature: float):
        """
        Sets the target temperature of the environmental chamber.

        Args:
            `temperature`: The target temperature to set in Celsius.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                target temperature.
        """
        # sets the temp of the chamber, temperature
        _LOGGER.debug(f"Setting target temperature to {temperature}°C")
        response = self._chamber.query(
            f"TEMP, S{temperature:.1f}", delay=self.SETTING_COMMAND_DELAY  # noqa E231
        )

        # verify the response
        response_pattern = re.compile(r"OK:TEMP, S\d+.\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the target temperature")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the target temperature")

    def set_target_humidity(self, humidity: Optional[float] = None):
        """
        Sets the target humidity of the environmental chamber.

        Args:
            `humidity`: The target humidity to set in percentage. If None, the humidity
                control is disabled.

        Raises:
            `ClimateChamberSettingError`: If an error occurred when setting the
                target humidity.
        """
        if humidity is None:
            _LOGGER.debug("Disabling humidity control")
            response = self._chamber.query(
                "HUMI, SOFF", delay=self.SETTING_COMMAND_DELAY
            )
            response_pattern = re.compile(r"OK:HUMI, SOFF")
        else:
            # sets the humidity of the chamber, (float) humidity
            _LOGGER.debug(f"Setting target humidity to {humidity}%")
            response = self._chamber.query(
                f"HUMI, S{humidity}", delay=self.SETTING_COMMAND_DELAY
            )
            response_pattern = re.compile(r"OK:HUMI, S\d+.*\d*")

        # verify the response
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the target humidity")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the target humidity")

    def close(self):
        """
        Closes the connection to the environmental chamber.
        """
        _LOGGER.debug("Closing the connection to the environmental chamber")
        self._chamber.close()

    def get_test_area_state(self) -> TestAreaState:
        """
        Get the chamber test area state.
        """
        response: str = self._chamber.query("MON?", delay=self.MONITOR_COMMAND_DELAY)

        # output data format: [temp, humid, op-state, num. of alarms]
        pattern = re.compile(
            r"(?P<temp>\d+\.\d+),(?P<humid>\d+),(?P<state>\w+),(?P<alarms>\d+)"
        )

        match = pattern.match(response)
        if match is None:
            _LOGGER.error("Failed to get the test area state")
            _LOGGER.debug(f"Response: '{response}'")
            raise MonitorError("Failed to get the test area state")

        test_area_state = TestAreaState(
            current_temperature=float(match["temp"]),
            current_humidity=float(match["humid"]),
            operation_state=OperationMode.from_str(match["state"]),
            number_of_alarms=int(match["alarms"]),
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
        _LOGGER.debug(
            f"Setting temperature limits to {upper_limit}°C and {lower_limit}°C"
        )
        response = self._chamber.query(f"TEMP, H{upper_limit: 0.1f}")

        response_pattern = re.compile(r"OK:TEMP, H \d+.\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the upper temperature limit")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the upper temperature limit")

        response = self._chamber.query(f"TEMP, L{lower_limit: 0.1f}")

        response_pattern = re.compile(r"OK:TEMP, L \d+.\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the lower temperature limit")
            _LOGGER.debug(f"Response: '{response}'")
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

        response_pattern = re.compile(r"OK:HUMI, H\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the upper humidity limit")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the upper humidity limit")

        response = self._chamber.query("HUMI, L" + str(lower_limit))

        response_pattern = re.compile(r"OK:HUMI, L\d+")
        if not response_pattern.match(response):
            _LOGGER.error("Failed to set the lower humidity limit")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the lower humidity limit")

    def get_mode(self) -> OperationMode:
        """
        Gets the operation mode of the environmental chamber.
        """
        response = self._chamber.query("MODE?", delay=self.MONITOR_COMMAND_DELAY)
        pattern = re.compile(r"(?P<mode>\w+)")
        match = pattern.match(response)

        if match is None:
            _LOGGER.error("Failed to get the operation mode")
            _LOGGER.debug(f"Response: '{response}'")
            raise MonitorError("Failed to get the operation mode")

        return OperationMode.from_str(response)

    def set_mode(self, mode: OperationMode):
        """
        Sets the operation mode of the environmental chamber.

        Args:
            `mode`: The operation mode to set.
        """
        # sets the mode of the chamber:
        _LOGGER.debug(f"Setting operation mode to {mode}")
        response = self._chamber.query(
            f"MODE, {mode}", delay=self.SETTING_COMMAND_DELAY
        )

        response_pattern = re.compile(r"OK:MODE, (?P<mode>\w+)")
        match = response_pattern.match(response)
        if match is None:
            _LOGGER.error("Failed to set the operation mode")
            _LOGGER.debug(f"Response: '{response}'")
            raise SettingError("Failed to set the operation mode")

        set_mode = OperationMode.from_str(match["mode"])
        if set_mode != mode:
            _LOGGER.error(
                f"Operation mode not set correctly"
                f" (current: {match['mode']}, expected: {mode})"
            )
            _LOGGER.debug(f"Response: '{response}'")
            _LOGGER.debug(f"Mode: '{match['mode']}'")
            raise SettingError("Failed to set the operation mode")

        return response

    def set_constant_condition(
        self,
        temperature: float,
        humidity: Optional[float] = None,
        stable_time=60.0,
        poll_interval=1.0,
    ):
        """
        Sets the environmental chamber to a constant temperature and humidity condition
        and waits until the setpoints are reached and stable.

        Args:
            `temperature`: The temperature to set in Celsius.
            `humidity`: The humidity to set in percentage. Default is None (humidity
                control is disabled)
            `stable_time`: The time in seconds to wait until the setpoints are stable.
                Default is 60.
            `poll_interval`: The time in seconds to wait between each check.
                Default is 1.
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

            time.sleep(poll_interval)

    def get_heater_percentage(self) -> HeatersStatus:
        """
        Gets the output of the heaters
        """
        response = self._chamber.query("%?", delay=self.MONITOR_COMMAND_DELAY)

        pattern = re.compile(r"\d+,(?P<temp>\d+\.\d+),(?P<humid>\d+\.\d+)")
        match = pattern.match(response)

        if match is None:
            _LOGGER.error("Failed to get the heaters status")
            _LOGGER.debug(f"Response: '{response}'")
            raise MonitorError("Failed to get the heaters status")

        heaters = HeatersStatus(
            temperature_heater=float(match["temp"]),
            humidity_heater=float(match["humid"]),
        )

        return heaters

    def __del__(self):
        self.close()
