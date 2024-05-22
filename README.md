# climate_chamber - Climate Chamber Controller

This allows to interact with the climate chamber PR-3J from Espec.

## Installation

```bash
pip install git+https://gitlab.desy.de/leandro.lanzieri/climate_chamber.git
```
## Development

To develop the package first clone the repository and navigate to the folder:
```bash
git clone https://gitlab.desy.de/leandro.lanzieri/climate_chamber.git
cd climate_chamber
```

Now you need to install the development dependencies and the package itself. To do so,
you can create a virtual environment and install the package in testing mode:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .[testing]
```

### Testing and Pre-Commit

We use pre-commit to run static checks (e.g., linting and type checking).
To install it run:
```bash
pre-commit install
```
This will automatically run the checks before each commit only on the files that
are being committed.

#### Unit Tests

To run the unit tests, you can use the following command:
```bash
tox
```

#### Static Tests

To run the static tests, you can use the following command:
```bash
tox -e lint
```
