BIDSit
===========

The ``BIDSit`` project is a toolbox to organize MRI data into BIDS format written in Python.

Installation
------------
Install ``BIDSit`` and its core dependencies via pip::

    pip install BIDSit

Or install ``BIDSit`` by cloning GitHub, then move to where the toolbox is
housed in terminal ::

	cd path/to/BIDSit

Then run ``setup.py`` to install dependencies ::

	Python3 setup.py install
	

Dependencies
------------
All of the core dependencies of ``BIDSit`` will be installed by ``pip``.

BIDSit requires ``dcm2niiX`` to convert the DICOM and PAR/REC files to NIfTI files. ``dcm2niiX`` can be downloaded from as part of MRIcroGL’s graphical interface from ::
    <https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage#Download>
