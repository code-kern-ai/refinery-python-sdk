#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as file:
    long_description = file.read()

setup(
    name="kern-sdk",
    version="1.0.1",
    author="jhoetter",
    author_email="johannes.hoetter@kern.ai",
    description="Official SDK for the Kern AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/code-kern-ai/kern-python",
    keywords=["kern", "machine learning", "supervised learning", "python"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    package_dir={"": "."},
    packages=find_packages("."),
    install_requires=[
        "numpy==1.22.3",
        "pandas==1.4.2",
        "requests==2.27.1",
        "boto3==1.24.26",
        "botocore==1.27.26",
        "spacy==3.3.1",
        "wasabi==0.9.1",
    ],
    entry_points={
        "console_scripts": [
            "kern=kern.cli:main",
        ],
    },
)
