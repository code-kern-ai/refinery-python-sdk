#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as file:
    long_description = file.read()

setup(
    name="kern-sdk",
    version="0.0.3",
    author="jhoetter",
    author_email="johannes.hoetter@kern.ai",
    description="Official SDK for the Kern AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/code-kern-ai/kern-python",
    keywords=["kern", "machine learning", "supervised learning", "python"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    package_dir={"": "."},
    packages=find_packages("."),
    install_requires=[
        "certifi==2021.10.8",
        "charset-normalizer==2.0.12",
        "click==8.1.3",
        "idna==3.3",
        "numpy==1.22.3",
        "pandas==1.4.2",
        "pathspec==0.9.0",
        "platformdirs==2.5.2",
        "python-dateutil==2.8.2",
        "pytz==2022.1",
        "requests==2.27.1",
        "six==1.16.0",
        "tinycss2==1.1.1",
        "tomli==2.0.1",
        "typing_extensions==4.2.0",
        "urllib3==1.26.9",
        "wasabi==0.9.1",
    ],
    entry_points={
        "console_scripts": [
            "kern=cli:main",
        ],
    },
)
