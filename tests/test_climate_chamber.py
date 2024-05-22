from climate_chamber import ClimateChamber, OperationMode


def test_temperatures(resource_path, resource_manager):
    chamber = ClimateChamber(
        resource_path=resource_path, resource_manager=resource_manager
    )

    TARGET = 23.2
    LOWER = 20.0
    UPPER = 25.0

    chamber.set_target_temperature(TARGET)
    chamber.set_temperature_limits(upper_limit=UPPER, lower_limit=LOWER)

    temperature = chamber.get_temperature_status()

    assert temperature.lower_limit == LOWER
    assert temperature.upper_limit == UPPER
    assert temperature.target_temperature == TARGET


def test_humidities(resource_path, resource_manager):
    chamber = ClimateChamber(
        resource_path=resource_path, resource_manager=resource_manager
    )

    TARGET = 50.0
    LOWER = 40.0
    UPPER = 60.0

    chamber.set_target_humidity(TARGET)
    chamber.set_humidity_limits(upper_limit=UPPER, lower_limit=LOWER)

    humidity = chamber.get_humidity_status()

    assert humidity.lower_limit == LOWER
    assert humidity.upper_limit == UPPER
    assert humidity.target_humidity == TARGET


def test_modes(resource_path, resource_manager):
    chamber = ClimateChamber(
        resource_path=resource_path, resource_manager=resource_manager
    )

    chamber.set_mode(OperationMode.CONSTANT)
    assert chamber.get_mode() == OperationMode.CONSTANT

    chamber.set_mode(OperationMode.OFF)
    assert chamber.get_mode() == OperationMode.OFF

    chamber.set_mode(OperationMode.STANDBY)
    assert chamber.get_mode() == OperationMode.STANDBY

    chamber.set_mode(OperationMode.RUN)
    assert chamber.get_mode() == OperationMode.RUN


def test_constant_condition(resource_path, resource_manager):
    TARGET_TEMP = 23.0
    ACC_HUMI = 1.0
    TARGET_HUMI = 50.0
    ACC_HUMI = 1.0
    STABLE_TIME = 0.01

    chamber = ClimateChamber(
        resource_path=resource_path,
        resource_manager=resource_manager,
        temperature_accuracy=ACC_HUMI,
        humidity_accuracy=ACC_HUMI,
    )

    chamber.set_constant_condition(
        temperature=TARGET_TEMP,
        humidity=TARGET_HUMI,
        stable_time=STABLE_TIME,
        poll_interval=0.001,
    )

    temperature = chamber.get_temperature_status()
    humidity = chamber.get_humidity_status()

    assert temperature.target_temperature == TARGET_TEMP
    assert humidity.target_humidity == TARGET_HUMI

    assert TARGET_HUMI - ACC_HUMI <= humidity.current_humidity <= TARGET_HUMI + ACC_HUMI
    assert (
        TARGET_TEMP - ACC_HUMI
        <= temperature.current_temperature
        <= TARGET_TEMP + ACC_HUMI
    )
