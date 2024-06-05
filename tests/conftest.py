import pytest
from climate_chamber_mocker import ClimateChamberMocker
from pyvisa import ResourceManager
from pyvisa_mock.base.register import register_resource

from climate_chamber import ClimateChamber, OperationMode

RESOURCE_PATH = "MOCK0::mock1::INSTR"


def pytest_addoption(parser):
    parser.addoption(
        "--hil", action="store_true", help="Run tests on hardware-in-the-loop"
    )
    parser.addoption("--hil_hostname", help="Hostname of the device under test")


@pytest.fixture(scope="session")
def hil(request):
    return request.config.option.hil is not None and request.config.option.hil


@pytest.fixture(scope="session")
def hil_hostname(hil, request):
    if not hil:
        return None

    return request.config.option.hil_hostname


@pytest.fixture(scope="module")
def climate_chamber(hil, hil_hostname):
    if hil:
        chamber = ClimateChamber(
            hostname=hil_hostname,
        )
    else:
        mock_climate_chamber = ClimateChamberMocker()
        register_resource(RESOURCE_PATH, mock_climate_chamber)

        resource_manager = ResourceManager(visa_library="@mock")

        chamber = ClimateChamber(
            resource_path=RESOURCE_PATH, resource_manager=resource_manager
        )

    yield chamber

    chamber.set_mode(OperationMode.STANDBY)
