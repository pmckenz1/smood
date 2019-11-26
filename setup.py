#!/usr/bin/env python

import re
from setuptools import setup

# parse version from init.py
with open("smood/__init__.py") as init:
    CUR_VERSION = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        init.read(),
        re.M,
    ).group(1)

# setup installation
setup(
    name="smood",
    packages=["smood"],
    version=CUR_VERSION,
    author="Patrick McKenzie",
    author_email="p.mckenzie@columbia.edu",
    install_requires=[
        "numpy>=1.9",
        "os",
        "subprocess",
        "pygbif",
        "rasterio",
        "IPython",
        "shutil"
    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
