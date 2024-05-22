import pytest
from climate_chamber_mocker import ClimateChamberMocker
from pyvisa import ResourceManager
from pyvisa_mock.base.register import register_resource

RESOURCE_PATH = "MOCK0::mock1::INSTR"


@pytest.fixture(scope="module")
def resource_manager():
    rm = ResourceManager(visa_library="@mock")
    return rm


@pytest.fixture(scope="module")
def mock_climate_chamber():
    mock_chamber = ClimateChamberMocker()
    resource_path = RESOURCE_PATH
    register_resource(resource_path, mock_chamber)
    return mock_chamber


@pytest.fixture(scope="module")
def resource_path():
    return RESOURCE_PATH
