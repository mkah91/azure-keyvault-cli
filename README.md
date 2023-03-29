# Azure Keyvault CLI

## Installation

### Install with pip

To install the latest stable version, run:

```sh
pip3 install --index-url https://test.pypi.org/simple/ azure-keyvault-cli
```

If you want to have it globally available, make sure to run it in your global python environment.

## Contributing

### Installation

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Run: `poetry install`

If you get an error `No such file or directory: 'python'`. Try settings an alias for python3:

```sh
alias python=python3
```

or activate an existing virtual environment.

### Usage

Make sure the right virtual env is activated, then you can use the local version of the cli by running, e.g.:

```sh
azkv --help
```

### Testing

To run the tests, run:

```sh
poetry run pytest
# with coverage
poetry run pytest --cov=cli --cov-report=xml --cov-report=term-missing
```

### Formatting

To format the code, run:

```sh
poetry run black .
```

### Linting

To lint the code, run:

```sh
poetry run ruff .
```
