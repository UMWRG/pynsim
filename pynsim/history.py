import pickle
import json

def load(filename):
    """
        Take a filename, exported using network.export_history() and load it into a
        python object
    """

    f = open(filename, 'r')
   
    if filename.find('.json') > 0:
        obj = json.load(f)
    elif filename.find('.pickle') > 0:
        obj = pickle.load(f)

    return obj


def load_multiple(filenames):
    """
        Take a list of filenames, exported using network.export_history() and load it into alist of python objects.
    """
    sim_results = []

    for filename in filenames:
        sim_result = load(filename)
        sim_results.append(sim_result)

    return sim_results

class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getstate__(self): return self

    def __setstate__(self, d): self.update(d)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

