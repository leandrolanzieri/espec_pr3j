import pytest
from climate_chamber_mocker import ClimateChamberMocker
from pyvisa import ResourceManager
from pyvisa_mock.base.register import register_resource

from climate_chamber import ClimateChamber

RESOURCE_PATH = "MOCK0::mock1::INSTR"


@pytest.fixture(scope="module")
def climate_chamber():
    mock_climate_chamber = ClimateChamberMocker()
    register_resource(RESOURCE_PATH, mock_climate_chamber)

    resource_manager = ResourceManager(visa_library="@mock")

    chamber = ClimateChamber(
        resource_path=RESOURCE_PATH, resource_manager=resource_manager
    )
    return chamber
