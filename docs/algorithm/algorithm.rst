.. _algorithm:

Algorithm description
=======================

Algorithms work with a 2D grid that represents a map of individual objects (bees, walls, etc.).
The simulation takes place in discrete time in this 2D space.
The time points are represented by the tick method.
Call this method do one step of the algorithm.

Behavior is dependent on the values of the variables that can
be set and the obstacles on the map, as well as the temperature
that is on one particular map field and will be described below
(**Bold** are the variable set in constructor).

Map
-----
The objects are encoded in the matrix as follows:

- 0 - empty position
- 1 - bee goes up
- 2 - bee goes right
- 3 - bee goes down
- 4 - bee goes left
- 5 - wall
- 6 - heater
- 7 - cooler
- -1 - bee which select direction in the newt step
- -t - waiting bee for t tick

Positions outside the defined map act like a wall -
that is, you can not move or promote heat over the edges of the map.

HeatMap
---------
Heat spreads across the map in all eight directions (unlike bee movements)
and is calculated in real numbers.

- In the wall position, the temperature is not defined (NaN)

- The temperature of the heater is always T_heater

- The temperature of the cooler is always T_cooler

- In positions where are no bees, the temperature is calculated:

.. math::

    T = \textbf{T_env} + \textbf{k_temp} \cdot max(heating, 0) - max(cooling, 0)

    heating = \frac{1}{\text{dist_heater}} \cdot (\textbf{T_heater} \cdot \textbf{T_env})

    cooling = \frac{1}{\text{dist_cooler}} \cdot (\textbf{T_env} \cdot \textbf{T_cooler})


- distance dist_heater and dist_cooler is the distance of the nearest heater or cooler
  in steps of 8 directions, considering walls and other coolers / heaters as obstacles

- **k_temp** is an adjustable coefficient that influences the thermal
  conductivity of the environment

Bees
------

- The bee moves through a correlated random walk
  (with the probability of **p_changedir**, the direction of movement of the bee changes randomly by one of
  the remaining three directions, otherwise the direction of movement is maintained).
  If she did not move (initially or stopped) before,
  the direction of the next step is chosen randomly from all four directions.

- If a bee hits an obstacle (wall, heat / cold source)
  with probability **p_wall** stops,
  otherwise it rotates by 180 ° and continues to move in the next step.

- If a bee meets (encounters) another bee, the probability of **p_meet** stops,
  otherwise the next step continues moving.

- If the bee stops, it remains in place for a time t that depends on the position temperature,
  where it stands (see formula below). After t time expires, proceed to step 1.

- To calculate the stop time, we use the formula:

    .. math::
        t = int(\frac{\textbf{k_stay}}{(1 + abs(\textbf{T_ideal} - \textbf{T_local})))}


    **k_stay** is an adjustable coefficient

    **T_ideal** is the temperature that bees prefer

    **T_local** is the temperature of the current position of the bee

    **min_wait** minimum waiting time
