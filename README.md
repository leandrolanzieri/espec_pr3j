# climate_chamber - Climate Chamber Controller

This allows to interact with the climate chamber PR-3J from Espec.

## Installation

```bash
pip install git+https://gitlab.desy.de/leandro.lanzieri/climate_chamber.git
```

## Simple usage
```python
from climate_chamber import ClimateChamber

CLIMATE_CHAMBER_HOST = "mskclimate01"
chamber = ClimateChamber(hostname=CLIMATE_CHAMBER_HOST)

# set limits
chamber.set_temperature_limits(upper_limit=28.0, lower_limit=23.0)
chamber.set_humidity_limits(upper_limit=40.0, lower_limit=60.0)

# go to a constant condition and wait until it's stable
chamber.set_constant_condition(
    temperature=27.0,
    humidity=50.0
)
```

## Feel like contributing?

Please check [our contribution guidelines](CONTRIBUTING.md), where you'll find how to set up your environment
and share your changes.
