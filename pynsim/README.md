PyNSim
========

Pynsim is a lightweight framework for building resource network simulations.
Through a resource object's setup function and its ability to support multiple 'Engines',
pynsim can support agent-based modelling and the integration of multiple models from different
backgrounds into a single simulation.

For documentation, see [here](http://umwrg.github.io/pynsim/).

Installation
============

    $ pip install pynsim

To test, in a python interpreter:

    >> from pynsim import Simulator
    >> s = Simulator()
    >> s.start()
