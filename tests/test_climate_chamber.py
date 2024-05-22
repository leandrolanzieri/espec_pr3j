from climate_chamber import ClimateChamber, OperationMode

TARGET_TEMPERATURE = 23.0
LOWER_TEMPERATURE = 20.0
UPPER_TEMPERATURE = 25.0

TARGET_HUMIDITY = 50.0
LOWER_HUMIDITY = 40.0
UPPER_HUMIDITY = 60.0

STABILITY_POLL_INTERVAL = 0.001
STABILITY_TIME = 0.01


def test_temperature_limits(climate_chamber: ClimateChamber):
    climate_chamber.set_temperature_limits(
        upper_limit=UPPER_TEMPERATURE, lower_limit=LOWER_TEMPERATURE
    )

    temperature = climate_chamber.get_temperature_status()

    assert temperature.lower_limit == LOWER_TEMPERATURE
    assert temperature.upper_limit == UPPER_TEMPERATURE


def test_humidity_limits(climate_chamber: ClimateChamber):
    climate_chamber.set_humidity_limits(
        upper_limit=UPPER_HUMIDITY, lower_limit=LOWER_HUMIDITY
    )

    humidity = climate_chamber.get_humidity_status()

    assert humidity.lower_limit == LOWER_HUMIDITY
    assert humidity.upper_limit == UPPER_HUMIDITY


def test_modes(climate_chamber: ClimateChamber):
    climate_chamber.set_mode(OperationMode.CONSTANT)
    assert climate_chamber.get_mode() == OperationMode.CONSTANT

    climate_chamber.set_mode(OperationMode.OFF)
    assert climate_chamber.get_mode() == OperationMode.OFF

    climate_chamber.set_mode(OperationMode.STANDBY)
    assert climate_chamber.get_mode() == OperationMode.STANDBY

    climate_chamber.set_mode(OperationMode.RUN)
    assert climate_chamber.get_mode() == OperationMode.RUN


def test_constant_condition(climate_chamber: ClimateChamber):
    climate_chamber.set_constant_condition(
        temperature=TARGET_TEMPERATURE,
        humidity=TARGET_HUMIDITY,
        stable_time=STABILITY_TIME,
        poll_interval=STABILITY_POLL_INTERVAL,
    )

    temperature = climate_chamber.get_temperature_status()
    humidity = climate_chamber.get_humidity_status()

    assert (
        abs(temperature.current_temperature - TARGET_TEMPERATURE)
        < climate_chamber.temperature_accuracy
    )
    assert (
        abs(humidity.current_humidity - TARGET_HUMIDITY)
        < climate_chamber.humidity_accuracy
    )


def test_test_area_state(climate_chamber: ClimateChamber):
    test_area = climate_chamber.get_test_area_state()

    assert (
        abs(test_area.current_temperature - TARGET_TEMPERATURE)
        < climate_chamber.temperature_accuracy
    )

    assert (
        abs(test_area.current_humidity - TARGET_HUMIDITY)
        < climate_chamber.humidity_accuracy
    )

    assert test_area.operation_state == OperationMode.CONSTANT
