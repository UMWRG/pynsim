from pynsim import Simulator, Network, Node, Engine
import unittest


class CountEngine(Engine):
    def __init__(self, *args, **kwargs):
        super(CountEngine, self).__init__(*args, **kwargs)
        self.run_count = None

    def initialise(self):
        self.run_count = 0

    def run(self):
        self.run_count += 1


class StopperEngine(Engine):
    def __init__(self, *args, **kwargs):
        self.stop_on_iteration = kwargs.pop('stop_on_iteration', 1)
        super(StopperEngine, self).__init__(*args, **kwargs)

    def run(self):
        if self.iteration >= self.stop_on_iteration:
            raise StopIteration()


class TypeErrorEngine(Engine):
    def __init__(self, *args, **kwargs):
        self.error_on_iteration = kwargs.pop('error_on_iteration', 1)
        super(TypeErrorEngine, self).__init__(*args, **kwargs)

    def run(self):
        if self.iteration >= self.error_on_iteration:
            raise TypeError('Something went wrong!')


class TestIteration(unittest.TestCase):
    """ Test simulator iteration settings. """
    def test_default_iteration(self):
        """ Test that the default simulation `max_iterations` is one. """
        s = Simulator()
        s.network = Network("Iteration test network")
        engine = CountEngine(None)
        s.add_engine(engine)

        s.timesteps = [0, ]
        s.start()

        assert engine.iteration == 1
        assert engine.run_count == 1

    def test_engine_iteration(self):
        """ Test setting the global number of iterations in a simulator. """
        s = Simulator(max_iterations=5)
        s.network = Network("Iteration test network")
        engine = CountEngine(None)
        s.add_engine(engine)

        s.timesteps = [0, ]
        s.start()

        assert engine.iteration == 5
        assert engine.run_count == 5

    def test_engine_stopping_iteration(self):
        """ Test an engine terminating iteration

        The engine must raise a `StopIteration` exception.
        """
        s = Simulator(max_iterations=5)
        s.network = Network("Iteration test network")

        stopper_engine = StopperEngine(None, stop_on_iteration=2)
        s.add_engine(stopper_engine)
        engine = CountEngine(None)
        s.add_engine(engine)

        s.timesteps = [0, ]
        s.start()

        assert engine.iteration == 1
        assert engine.run_count == 1
        assert stopper_engine.iteration == 2

    def test_engine_error(self):
        """ Test an engine can raises a non-StopIteration error.
        """
        s = Simulator(max_iterations=5)
        s.network = Network("Iteration test network")

        s.add_engine(TypeErrorEngine(None, error_on_iteration=1))
        s.add_engine(CountEngine(None))
        s.timesteps = [0, ]

        with self.assertRaises(TypeError):
            s.start()


if __name__ == '__main__':
    unittest.main()

