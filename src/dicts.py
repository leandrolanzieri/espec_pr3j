from enum import Enum
from typing import TypedDict


class TemperatureStatus(TypedDict):
    """
    The temperature status of the climate chamber. All values are in Celsius.
    """

    current_temperature: float
    """The current temperature of the climate chamber"""

    target_temperature: float
    """The target temperature of the climate chamber"""

    upper_limit: float
    """The upper temperature limit of the climate chamber"""

    lower_limit: float
    """The lower temperature limit of the climate chamber"""


class HumidityStatus(TypedDict):
    """
    The humidity status of the climate chamber. All values are in percentage.
    """

    current_humidity: float
    """The current humidity of the climate chamber"""

    target_humidity: float
    """The target humidity of the climate chamber"""

    upper_limit: float
    """The upper humidity limit of the climate chamber"""

    lower_limit: float
    """The lower humidity limit of the climate chamber"""


class HeatersStatus(TypedDict):
    """
    The status of the heaters. All values are in percentage.
    """

    temperature_heater: float
    """The output of the temperature heater"""

    humidity_heater: float
    """The output of the humidity heater"""


class OperationMode(Enum):
    """
    The operation mode of the climate chamber.
    """

    OFF = "OFF"
    """The panel is powered off"""

    CONSTANT = "CONSTANT"
    """Constant operation"""

    STANDBY = "STANDBY"
    """All operations are stopped"""

    RUN = "RUN"
    """A program is running"""

    @classmethod
    def from_str(cls, value: str) -> "OperationMode":
        """
        Convert a string to an OperationMode.

        Args:
            value: The string to convert. The string is case-insensitive.
        """
        return cls[value.upper()]

    def __str__(self) -> str:
        return self.value


class TestAreaState(TypedDict):
    """
    The state of the test area.
    """

    current_temperature: float
    """The current temperature of the test area, in Celsius"""

    current_humidity: float
    """The current humidity of the test area, in percentage"""

    operation_state: OperationMode
    """The operation state"""

    number_of_alarms: int
    """The number of alarms occurring"""
