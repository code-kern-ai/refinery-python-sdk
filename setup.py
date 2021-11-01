#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as file:
    long_description = file.read()

setup(
    name="onetask",
    version="0.1.14",
    author="onetask",
    author_email="info@onetask.ai",
    description="Official Python SDK for the onetask API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onetask-ai/onetask-python",
    keywords=["onetask", "machine learning", "supervised learning", "python"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    package_dir={"": "."},
    packages=find_packages("."),
    install_requires=[
        "transformers==4.12.2",
        "torch==1.10.0",
        "torchvision==0.11.1",
        "torchaudio==0.10.0",
        "nltk==3.6.5",
        "scikit-learn==1.0.1",
        "certifi==2021.5.30",
        "spacy==3.1.3",
        "pandas==1.3.3",
        "chardet==4.0.0",
        "idna==2.10",
        "requests==2.25.1",
        "urllib3==1.26.5",
        "wasabi==0.8.2",
    ],
)
