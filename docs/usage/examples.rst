.. _examples:

Examples
============


.. testsetup::


    import numpy
    from beeclust.beeclust import BeeClust
    referencion = BeeClust(numpy.zeros((4,4), dtype = numpy.int8))

The parrot module is a module about parrots.

Doctest example:

.. doctest::

    >>> simulation = BeeClust(numpy.zeros((4,4), dtype = numpy.int8))
    >>> simulation.tick()
    0

Test-Output example:

.. testcode::

    simulation.tick()

This would output:

.. testoutput::

    0

You can use other values:

.. testcode::

    simulation.tick()

.. testoutput::
   :hide:

    0
