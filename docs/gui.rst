.. _gui:

Application GUI
=======================

In the **BeeClust**, a GUI is also created to visualize the algorithm simulation.
The GUI is created in the PyQt5 framework.
With GUI, it is also possible to save and retrieve simulation from a file.

In the GUI, you can create a new blank simulation.
It is then possible to drag and drop items into this simulation.
In edit, you can edit simulation parameters.

You can zoom in and out (Ctrl + mouse wheel) within certain limits.
In the toolbar, we can capture the graphical
view of the heat map or perform the simulation steps (also with the space bar).

Run
------
**BeeClust** can be run in GUI mode. To install is need clone and build Cython.
Script is need run at least on python 3.6 and more:

- Clone **BeeClust** from `repository <https://github.com/martilad/beeclust>`_.
- Go into the cloned directory.
- Run ``python -m pip install -r requirements.txt``
- Use the following command in the directory to build Cython code for your system: ``python setup.py build_ext --inplace``
- After build you can run with: ``python -m beeclust``