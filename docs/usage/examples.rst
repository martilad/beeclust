.. _examples:

Examples
============

Here are some examples of beahvior of beeclust and instructions how to use it.


.. testsetup::

   import numpy
   from beeclust.beeclust import BeeClust
   referencion = BeeClust(numpy.zeros((5,5), dtype = numpy.int8))

Basic examples
----------------


Init the algorithm
~~~~~~~~~~~~~~~~~~~~~~

You can create map as numpy array and add some map item to it. 

Set probability of change direction to 0 and probability stop when hit the wall and other bee to 0 too. 
This do deterministic behavior of two bees in map in examples. Creation of map and init algorithm: 


.. doctest::

   >>> map = numpy.zeros((2,2), dtype = numpy.int8)
   >>> map[1, 1] = 1
   >>> simulation = BeeClust(map, p_changedir = 0, p_wall = 0, T_env=10)
   >>> simulation.bees
   [(1, 1)]

Tick examples 
~~~~~~~~~~~~~~~~~~~~~~

The bee should move in line from up to down of the map. 
Tick return the number of bees which moved.
Bellow is example when bee moved up and hit the end of the map and move down in the oposite direction.

.. doctest::

   >>> simulation.tick()
   1
   >>> simulation.bees
   [(0, 1)]
   >>> simulation.tick()
   0
   >>> simulation.bees
   [(0, 1)]
   >>> simulation.tick()
   1
   >>> simulation.bees
   [(1, 1)]

HeatMap
~~~~~~~~~~~~~~~~~~~~~~

Next what you can see, is that heat map in enviroment where there are not heaters and coolers is the T_env. Try add some heater and cooler and recalculate heatmap.

.. doctest::

   >>> print(simulation.heatmap)
   [[10. 10.]
    [10. 10.]]
   >>> simulation.map[0,0] = 6
   >>> simulation.map[1,0] = 7
   >>> simulation.T_heater = 20
   >>> simulation.T_cooler = -5
   >>> print(simulation.heatmap)
   [[10. 10.]
    [10. 10.]]
   >>> simulation.recalculate_heat()
   >>> print(simulation.heatmap)
   [[20.   5.5]
    [-5.   5.5]]


Swarms and score
~~~~~~~~~~~~~~~~~~~~~~
And when you try to get swarms and print:

.. testcode::

   print(simulation.swarms)

You get one swarm with one bee:

.. testoutput::
   
   [[(1, 1)]]

And score on the change heatmap:

.. testcode::

   print(simulation.score)

It is definitely be:

.. testoutput::

   5.5

Forget
~~~~~~~~~~~~~~~~~~~~~~

When use forget, the bees forget they direction, so the bee have value -1 and after tick not move and select the direction.

.. doctest::

   >>> simulation.forget()
   >>> simulation.map[simulation.bees[0]]
   -1
   >>> simulation.tick()
   0



Next examples of usage
------------------------





Test-Output example:

.. testcode::

   print(referencion.tick())

This would output:

.. testoutput::
   
   0


You can use other values:

.. testcode::

   print(referencion.score)

.. testoutput::
   :hide:

   0


