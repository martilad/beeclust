.. beeclust documentation master file, created by
   sphinx-quickstart on Mon Nov 26 11:35:43 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Beeclust's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   gui
   algorithm/algorithm
   usage/instalation
   usage/examples
   auto/api
   license


Introduction
==================
Beeclust is an algorithm to simulate the behavior of bees in the environment.
The algorithm was introduced in the article
`BEECLUST: A Swarm Algorithm Derived from
Honeybees.
Derivation of the Algorithm, Analysis by
Mathematical Models
and Implementation on a Robot Swarm
<http://heikohamann.de/pub/schmickl_beeclust_2011.pdf>`_.

This algorithm is implemented as importable python class,
in which is simulated the clustering. The algorithm is based on bee behavior in nature.
Bees in nature swarm in places with ideal temperatures (approximately 32-38 °C).

The algorithm can be easily used in practice for working with simple autonomous robots.
The individual bees same as robots have no memory and information about the environment.
Changes are based on some probabilities.
Each bee cant meet other bee or barrier which stop it.
If the bee does not move, its waiting time is temperature dependent.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`