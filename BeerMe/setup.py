import os
from setuptools import setup, find_packages


def readme():
    """Utility function to read the README file. Used for the long_description."""
    with open('README.md') as f:
        return f.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="BeerMe",
    version="0.1",
    author="Tom Sharp",
    author_email="tom.m.sharp12@gmail.com",
    description=("A beer to find the right app... wait no"),
    long_description=readme(),
    url="https://github.com/tmsharp/BeerMe",
    packages=find_packages("."),
    install_requires=required,
)