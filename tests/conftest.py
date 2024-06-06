import pytest
from espec_pr3j_mocker import EspecPr3jMocker
from pyvisa import ResourceManager
from pyvisa_mock.base.register import register_resource

from espec_pr3j import EspecPr3j, OperationMode

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
def environmental_chamber(hil, hil_hostname):
    if hil:
        chamber = EspecPr3j(
            hostname=hil_hostname,
        )
    else:
        mock_environmental_chamber = EspecPr3jMocker()
        register_resource(RESOURCE_PATH, mock_environmental_chamber)

        resource_manager = ResourceManager(visa_library="@mock")

        chamber = EspecPr3j(
            resource_path=RESOURCE_PATH, resource_manager=resource_manager
        )

    yield chamber

    chamber.set_mode(OperationMode.STANDBY)
