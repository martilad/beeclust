.. _instalation:

Build for usage
========================


**BeeClust** can be use as importable module. To install is need clone and build Cython.
Script is need run at least on python 3 and more:

- Clone **BeeClust** from `repository <https://github.com/martilad/beeclust>`_.
- Go into the cloned directory.
- Use the following command in the directory to build Cython code for your system: ``python setup.py build_ext --inplace``
- After build you can use import from module to use this algorithm: ``from beeclust import BeeClust``
- For class documentation see :ref:`BeeClust`