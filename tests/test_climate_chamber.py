from climate_chamber import ClimateChamber


def test_set_temperatures(resource_path, resource_manager, mock_climate_chamber):
    chamber = ClimateChamber(
        resource_path=resource_path, resource_manager=resource_manager
    )

    TARGET = 23.2
    LOWER = 20.0
    UPPER = 25.0
    CURRENT = 21.8

    chamber.set_target_temperature(TARGET)
    chamber.set_temperature_limits(upper_limit=UPPER, lower_limit=LOWER)

    # simulate temperature measurement
    mock_climate_chamber.set_current_temperature(CURRENT)

    temperature = chamber.get_temperature_status()

    assert temperature.current_temperature == CURRENT
    assert temperature.lower_limit == LOWER
    assert temperature.upper_limit == UPPER
    assert temperature.target_temperature == TARGET


def test_set_humidities(resource_path, resource_manager, mock_climate_chamber):
    chamber = ClimateChamber(
        resource_path=resource_path, resource_manager=resource_manager
    )

    TARGET = 50.0
    LOWER = 40.0
    UPPER = 60.0
    CURRENT = 45.0

    chamber.set_target_humidity(TARGET)
    chamber.set_humidity_limits(upper_limit=UPPER, lower_limit=LOWER)

    # simulate humidity measurement
    mock_climate_chamber.set_current_humidity(CURRENT)

    humidity = chamber.get_humidity_status()

    assert humidity.current_humidity == CURRENT
    assert humidity.lower_limit == LOWER
    assert humidity.upper_limit == UPPER
    assert humidity.target_humidity == TARGET
