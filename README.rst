BeeClust
=========
|travis|

.. |travis| image:: https://travis-ci.com/martilad/beeclust.svg?token=zi6LcxYGEfNZWAzqS8CX&branch=master
    :target: https://travis-ci.com/martilad/beeclust

**BeeClust** is an algorithm to simulate the behavior of bees in the environment.
It is created as a part of **MI-PYT** course at **CTU in Prague**.


Build for usage
-----------------

**BeeClust** can be use as importable module. To install is need clone and build Cython.
Script is need run at least on python 3 and more:

1. Clone **BeeClust** from `repository <https://github.com/martilad/beeclust>`_.
2. Go into the cloned directory.
3. Run ``python -m pip install -r requirements.txt``
4. Use the following command in the directory to build Cython code for your system: ``python setup.py build_ext --inplace``
5. You can import from module beeclust


Documentation
--------------

The documentation can build using the following steps:

1. Clone **BeeClust** from `repository <https://github.com/martilad/beeclust>`_.
2. Go to **docs** directory inside the **BeeClust**.
3. Run ``python -m pip install -r requirements.txt``
4. Run ``make html`` and ``make doctest``
5. You can find all of the .html files in _build/html directory

License
-------------

This project is licensed under the **MIT License**.