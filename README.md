# Azure Keyvault CLI

## Installation

### Install with pip

If you want to have it globally available, run in your global python environment:

```
pip3 install --index-url https://test.pypi.org/simple/ azure-keyvault-cli
```


## Contributing

### Installation

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Run: `poetry install`

If you get an error `No such file or directory: 'python'`. Try settings an alias for python3:

```
alias python=python3
```

or activate an existing virtual environment.

### Usage

Make sure the right virtual env is activated, then you can use the local version of the cli by running, e.g.:

```
azkv --help
```