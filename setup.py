import io
import os
from setuptools import find_packages, setup

def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content

setup(
    name="Azure Keyvault CLI",
    version="0.1.0",
    url="https://github.com/mkah91/azure-keyvault-cli",
    author="mkah91",
    author_email="marius_knepper@web.de",
    license="MIT",
    keywords="azure keyvault secrets cli",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", ".github"]),
    include_package_data=True,
    install_requires=[
        "azure-identity==1.12.0",
        "azure-keyvault-secrets==4.7.0",
        "click==8.1.3",
        "inquirerpy==0.3.4",
        "pyperclip==1.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "twine>=4.0.2",
        ],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "azkv = cli.main:azkv",
        ],
    },
)
