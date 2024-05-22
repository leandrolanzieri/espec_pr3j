from pyvisa_mock.base.base_mocker import BaseMocker, scpi


class ClimateChamberMocker(BaseMocker):
    """
    A mocker for a climate chamber.
    """

    def __init__(self, call_delay: float = 0.0):
        super().__init__(call_delay=call_delay)
        self._target_temperature = 0.0
        self._current_temperature = 0.0
        self._lower_temperature = 0.0
        self._upper_temperature = 0.0

        self._target_humidity = 0.0
        self._current_humidity = 0.0
        self._lower_humidity = 0.0
        self._upper_humidity = 0.0

    @scpi("TEMP, S<temperature>")
    def _set_target_temperature(self, temperature: float) -> str:
        self._target_temperature = temperature
        return f"OK: TEMP, S{temperature}\r\n"

    @scpi("TEMP, H<temperature>")
    def _set_upper_temperature(self, temperature: float) -> str:
        self._upper_temperature = temperature
        return f"OK: TEMP, H{temperature}\r\n"

    @scpi("TEMP, L<temperature>")
    def _set_lower_temperature(self, temperature: float) -> str:
        self._lower_temperature = temperature
        return f"OK: TEMP, L{temperature}\r\n"

    @scpi("TEMP?")
    def _get_temperature_status(self) -> str:
        response = f"{self._current_temperature}"
        response += f", {self._target_temperature}"
        response += f", {self._upper_temperature}"
        response += f", {self._lower_temperature}"

        return response

    @scpi("HUMI, S<humidity>")
    def _set_target_humidity(self, humidity: float) -> str:
        self._target_humidity = humidity
        return f"OK: HUMI, S{humidity}\r\n"

    @scpi("HUMI, H<humidity>")
    def _set_upper_humidity(self, humidity: float) -> str:
        self._upper_humidity = humidity
        return f"OK: HUMI, H{humidity}\r\n"

    @scpi("HUMI, L<humidity>")
    def _set_lower_humidity(self, humidity: float) -> str:
        self._lower_humidity = humidity
        return f"OK: HUMI, L{humidity}\r\n"

    @scpi("HUMI?")
    def _get_humidity_status(self) -> str:
        response = f"{self._current_humidity}"
        response += f", {self._target_humidity}"
        response += f", {self._upper_humidity}"
        response += f", {self._lower_humidity}"

        return response

    def set_current_temperature(self, temperature: float):
        """
        Set the current temperature of the chamber.
        """
        self._current_temperature = temperature

    def set_current_humidity(self, humidity: float):
        """
        Set the current humidity of the chamber.
        """
        self._current_humidity = humidity
