# Multi Scenario

This classes allows to manage simulations using multiscenario input data

## Enforcements requested

In order to make everything working properly, we need to be sure that:

- All Nodes MUST BE created directly by Pynsim classes or by classes subclasses from Pynsim classes
- All created nodes MUST BE registered to the simulator, and have properly defined the __setattr__ method


### Registration to the simulator

Whenever a new node is created, it has to be registered to the simulator through a registered network.
Every Node that is managed outside the simulator structure cannot be properly managed

### Setting attributes proxy

Whenever the developer needs to overload the node's __setattr__ method, the overload method have to contain the following row:

```python
def __setattr__(self, name, value):
  super().__setattr__(name, value)
  ....
```
