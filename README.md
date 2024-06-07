# espec_pr3j - Remote controller for the Espec PR-3J Environmental Chamber

This allows to interact remotely with the environmental chamber PR-3J from Espec.

## Installation

```bash
pip install espec-pr3j
```

## Simple usage
```python
from espec_pr3j import EspecPr3j

CHAMBER_HOST = "mskclimate3"
chamber = EspecPr3j(hostname=CHAMBER_HOST)

# set limits
chamber.set_temperature_limits(upper_limit=28.0, lower_limit=23.0)
chamber.set_humidity_limits(upper_limit=40.0, lower_limit=60.0)

# go to a constant condition and wait until it's stable
chamber.set_constant_condition(
    temperature=27.0,
    humidity=50.0
)
```

## Running tests on hardware

During normal development and for the CI the unit test suite is executed on a mock
device using pyvisa-mock. It is also possible to run tests on real hardware connected
to your system. Just set the `hil` flag when running `tox`, and pass the hostname:

```bash
$ tox -- --hil --hil_hostname mskclimate3
```

## Documentation

For more details of the module API, check the [online documentation].

## Feel like contributing?

Please check [our contribution guidelines](CONTRIBUTING.md), where you'll find how to set up your environment
and share your changes.

[online documentation]: https://climate-chamber-leandro-lanzieri-bcc388d1f7cfd484ca00bcced68d65.pages.desy.de/
