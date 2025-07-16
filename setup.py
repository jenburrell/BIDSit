#===============================================================================#
# Script Name: setup.py                                                         #
#                                                                               #
# Description: ensures all toolboxes necessary are downloaded for BIDSit        #
#                                                                               #
# Author:      Jen Burrell (April 17th, 2023)                                   #
#===============================================================================#
import os.path as op
from setuptools import setup
from setuptools import find_namespace_packages
from setuptools import Command

# - setup.py file's home directory - #
basedir = op.dirname(__file__)

# - Get Version - #
version = {}
with open(op.join(basedir, "src/BIDSit/version.py")) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break
version = version['__version__']

# - Readme - #
with open(op.join(basedir, 'README.rst'), 'rt') as f:
    readme = f.read()

# - Dependencies are listed in requirements.txt - #
#with open(op.join(basedir, 'requirements.txt'), 'rt') as f:
#    install_requires = [l.strip() for l in f.readlines()]

# - set it up! - #
setup(
    name='BIDSit',
    version=version,
    description='A BIDS conversion tool for fMRI data',
    long_description=readme,
    long_description_content_type='text/x-rst',
    url='https://github.com/jenburrell/BIDSit',
    author='Jen Burrell',
    author_email='jenbur@psych.ubc.ca',
    python_requires='>=3.9',
    
    package_dir={"":"src"},
    packages=find_namespace_packages(where='src'),
    
    classifiers=[
    'Programming Language :: Python :: 3.10',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    install_requires=[
        'FreeSimpleGUI>=5.2.0',
        'natsort>=8.3.1',
    ],
    extras_require={
        "dev": [
            "pytest>=3.7",
        ],
    },
    entry_points={
        'console_scripts': [
            'BIDSit = BIDSit.go:DOit',
        ]
    }
)

