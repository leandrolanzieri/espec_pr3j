from pyvisa_mock.base.base_mocker import BaseMocker, scpi


class ClimateChamberMocker(BaseMocker):
    """
    A mocker for a climate chamber.
    """

    LINE_TERMINATION = "\r\n"
    """The line termination character for the mocker."""

    def __init__(
        self,
        call_delay: float = 0.0,
        temperature_steps: int = 10,
        humidity_steps: int = 10,
    ):
        super().__init__(call_delay=call_delay)
        self._target_temperature = 0.0
        self._lower_temperature = 0.0
        self._upper_temperature = 0.0
        self._temperature_steps: list[float] = [0.0]
        self._temperature_num_steps = temperature_steps

        self._target_humidity = 0.0
        self._lower_humidity = 0.0
        self._upper_humidity = 0.0
        self._humidity_steps: list[float] = [0.0]
        self._humidity_num_steps = humidity_steps

        self._mode = "STANDBY"

    @scpi("TEMP, S<temperature>")
    def _set_target_temperature(self, temperature: float) -> str:
        self._target_temperature = temperature

        # we want to simulate a linear temperature change
        # calculate the step size based on the number of steps and difference
        current = self._current_temperature
        step_jump = temperature - current
        step_size = step_jump / self._temperature_num_steps

        self._temperature_steps = []
        for step in range(self._temperature_num_steps + 1):
            self._temperature_steps.append(current + step * step_size)

        return f"OK: TEMP, S{temperature}{self.LINE_TERMINATION}"

    @property
    def _current_temperature(self) -> float:
        # always return the last element of the list
        # pop it from the list, unless it is the last one
        if len(self._temperature_steps) > 1 and self._mode == "CONSTANT":
            return self._temperature_steps.pop(0)
        return self._temperature_steps[0]

    @scpi("TEMP, H<temperature>")
    def _set_upper_temperature(self, temperature: float) -> str:
        self._upper_temperature = temperature
        return f"OK: TEMP, H{temperature}{self.LINE_TERMINATION}"

    @scpi("TEMP, L<temperature>")
    def _set_lower_temperature(self, temperature: float) -> str:
        self._lower_temperature = temperature
        return f"OK: TEMP, L{temperature}{self.LINE_TERMINATION}"

    @scpi("TEMP?")
    def _get_temperature_status(self) -> str:
        response = f"{self._current_temperature:.1f}"  # noqa E231
        response += f", {self._target_temperature:.1f}"  # noqa E231
        response += f", {self._upper_temperature:.1f}"  # noqa E231
        response += f", {self._lower_temperature:.1f}"  # noqa E231
        response += f"{self.LINE_TERMINATION}"

        return response

    @scpi("HUMI, S<humidity>")
    def _set_target_humidity(self, humidity: float) -> str:
        self._target_humidity = humidity

        # we want to simulate a linear humidity change
        # calculate the step size based on the number of steps and difference
        current = self._current_humidity
        step_jump = humidity - current
        step_size = step_jump / self._humidity_num_steps

        self._humidity_steps = []
        for step in range(self._humidity_num_steps + 1):
            self._humidity_steps.append(current + step * step_size)

        return f"OK: HUMI, S{humidity}{self.LINE_TERMINATION}"

    @property
    def _current_humidity(self) -> float:
        # always return the last element of the list
        # pop it from the list, unless it is the last one
        if len(self._humidity_steps) > 1 and self._mode == "CONSTANT":
            return self._humidity_steps.pop(0)

        return self._humidity_steps[0]

    @scpi("HUMI, H<humidity>")
    def _set_upper_humidity(self, humidity: float) -> str:
        self._upper_humidity = humidity
        return f"OK: HUMI, H{humidity}\r\n"

    @scpi("HUMI, L<humidity>")
    def _set_lower_humidity(self, humidity: float) -> str:
        self._lower_humidity = humidity
        return f"OK: HUMI, L{humidity}{self.LINE_TERMINATION}"

    @scpi("HUMI?")
    def _get_humidity_status(self) -> str:
        response = f"{self._current_humidity:.1f}"  # noqa E231
        response += f", {self._target_humidity:.1f}"  # noqa E231
        response += f", {self._upper_humidity:.1f}"  # noqa E231
        response += f", {self._lower_humidity:.1f}"  # noqa E231
        response += f"{self.LINE_TERMINATION}"

        return response

    @scpi("MODE, <mode>")
    def _set_mode(self, mode: str) -> str:
        if mode not in ["STANDBY", "OFF", "CONSTANT", "RUN"]:
            return f"NA:DATA NOT READY{self.LINE_TERMINATION}"  # noqa E231

        self._mode = mode
        return f"OK: MODE, {mode}{self.LINE_TERMINATION}"

    @scpi("MODE?")
    def _get_mode(self) -> str:
        return self._mode

    @scpi("MON?")
    def _get_monitor(self) -> str:
        response = f"{self._current_temperature:.1f}"  # noqa E231
        response += f", {self._current_humidity:.1f}"  # noqa E231
        response += f", {self._mode}"
        response += ", 0"  # number of alarms occurring
        response += f"{self.LINE_TERMINATION}"

        return response
