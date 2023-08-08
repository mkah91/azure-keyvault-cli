[![End-to-End Test](https://github.com/mkah91/azure-keyvault-cli/actions/workflows/e2e-test.yaml/badge.svg)](https://github.com/mkah91/azure-keyvault-cli/actions/workflows/e2e-test.yaml)

# Azure KeyVault CLI

This is a CLI tool to interact with an Azure KeyVault. You can use it to easily list and show secrets. Additionally, you can use it to check the expiration date of all the secrets in your KeyVault.

## Installation

### Install with pip
To install the latest stable version from [PyPI](https://pypi.org/project/azure-keyvault-cli/), run:

```sh
pip3 install azure-keyvault-cli
```


To install the latest version (potentially not stable) from [TestPyPI](https://test.pypi.org/project/azure-keyvault-cli/), run:

```sh
pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple azure-keyvault-cli
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

### Releasing

#### Bump version

First, bump the version in the `pyproject.toml` file. You can do this manually or by running:

```sh
poetry version <major|minor|patch>
```

Then commit the changes and push them to the remote repository. Additionally, add a tag to the commit with the new version number. You can do this by running:

```sh
version=$(poetry version --short)
git checkout -b release-${version}
git add pyproject.toml
git commit -m "Bump version to ${version}"
git push --set-upstream origin release-${version}
git tag -a ${version} -m "Release ${version}"
git push origin ${version}
```

#### Create pull request

Create a pull request from the release branch to the main branch. The pull request will trigger the test workflow. The workflow will run the tests and check the formatting and linting of the code. You can create a pull request by running:

```sh
version=$(poetry version --short)
gh pr create --title "Release ${version}" --body "Release ${version}" --base main --head release-${version}
```

#### Create release

After the pull request has been merged, the release workflow will be triggered. The workflow will create a new release and publish the package to [PyPI](https://test.pypi.org/project/azure-keyvault-cli/). Be aware that this workflow needs to be manually approved before it will be executed.
