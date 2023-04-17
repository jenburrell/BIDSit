BIDSit
===========

The ``BIDSit`` project is a toolbox to organize MRI data into BIDS format written in Python.

Installation
------------
Install ``BIDSit`` and its core dependencies via pip::

    pip install BIDSit

Install ``BIDSit`` by cloning GitHub, then move to where the toolbox is
housed in terminal ::

	cd path/to/BIDSit

Then run ``setup.py`` to install dependencies ::

	Python3 setup.py install
	

Dependencies
------------
All of the core dependencies of ``BIDSit`` will be installed by ``pip``.

To install ``BIDSit``, along with all the tools you need to develop
and run tests run the following in your virtualenv ::

	pip install -e .[dev] 
