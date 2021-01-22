#!/usr/bin/env python
from io import open
from setuptools import setup

version = "0.1.0"

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="prettydiff",
    version=version,
    author="python273",
    author_email="prettydiff@python273.pw",
    description="Pretty JSON data diffs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/python273/prettydiff",
    download_url="https://github.com/python273/prettydiff/archive/v{}.zip".format(
        version
    ),
    license="MIT",
    packages=["prettydiff"],
    install_requires=[],
    extras_require={"terminal": ["colorama"]},
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
