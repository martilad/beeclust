.. _examples:

Examples
============

Here are some examples of behavior of because and instructions how to use it.


.. testsetup::

   import numpy
   from beeclust.beeclust import BeeClust
   referencion = BeeClust(numpy.zeros((5,5), dtype = numpy.int8), p_changedir = 0, p_wall = 0, T_env=10, p_meet = 1, T_ideal = 10)
   referencion.map[2, 3] = 2
   referencion.map[1, 2] = 1
   referencion.map[2, 2] = 3
   referencion.map[3, 2] = 3
   referencion.map[2, 1] = 4

Basic examples
----------------
Here are some basic examples with one bee.

Init the algorithm
~~~~~~~~~~~~~~~~~~~~~~

You can create the map as numpy array and add some map item to it.

I set the probability of change direction to 0 and probability stop when hitting the wall to 0 too.
These steps do deterministic behavior of two bees in the map in examples. Creation of map and init algorithm:


.. doctest::

   >>> map = numpy.zeros((2,2), dtype = numpy.int8)
   >>> map[1, 1] = 1
   >>> simulation = BeeClust(map, p_changedir = 0, p_wall = 0, T_env=10)
   >>> simulation.bees
   [(1, 1)]

Tick examples 
~~~~~~~~~~~~~~~~~~~~~~

The bee should move in a line from up to down of the map.
Tick return the number of bees which moved.
Bellow is an example when bee moved up and hit the end of the map and move down in the opposite direction.

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

Next what you can see, is that heat map in the environment where there are not heaters and coolers is the T_env.
Try to add some heater and cooler and recalculate heatmap.

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

It is definitely:

.. testoutput::

   5.5

Forget
~~~~~~~~~~~~~~~~~~~~~~

When use forgets, the bees forget they direction,
so the bee have value -1 and after tick not move and select the direction.

.. doctest::

   >>> simulation.forget()
   >>> simulation.map[simulation.bees[0]]
   -1
   >>> simulation.tick()
   0



Next examples of usage
------------------------

I introduce one more example with more bees.

I have created map 5x5 with five bees in the middle. All bee move from the center.
So I set change_dir and wall to 0 and meet to 1.
So simulated three steps show that all bee will be in one cluster in the middle.

Let's see the map:

.. doctest::

    print(referencion.map)

This would output:

.. testoutput::

   [[0 0 0 0 0]
    [0 0 1 0 0]
    [0 4 3 2 0]
    [0 0 3 0 0]
    [0 0 0 0 0]]

Now do three tick and check the number of swarms, all bees are back in the middle in the swarm:

.. testcode::

   print(referencion.tick())
   print(referencion.tick())
   print(referencion.tick())
   print(len(referencion.swarms))


.. testoutput::

   4
   0
   4
   1

