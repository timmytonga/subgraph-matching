""" by Tim Nguyen
    Supernodes class: a container type to hold the candidates as well as some special attributes
    for matching --> including equivalent classes !!! """


class Supernode(object):
    """An object to hold equivalent classes and sets of nodes
    for other data structure. Special is that it sorts the equiv_class
    into a tuple for hashing and comparing if we store supernodes in a dictionary/set for example"""

    channels = []  # class attribute: a list of channels. Initialized in main

    def __init__(self, equiv_class: list or set or tuple, name: str=None):
        """ Note that equiv_class should be either a set, list or tuple """
        try:
            self.vertices = tuple(sorted(equiv_class))  # for ease of comparing
        except TypeError:  # maybe better checks here
            self.vertices = tuple([equiv_class])
        if name is None:
            self.name = str(self.vertices)
        else:
            self.name = name  # ideally the tuple with the real name

    def get_vertices(self) -> tuple:
        """ returns a tuple of vertices of the equiv class of the supernode"""
        return self.vertices

    def get_set_of_vertices(self) -> set:
        return set(self.vertices)

    def __len__(self):
        """ Returns the number of template node it contains """
        return len(self.vertices)

    def __hash__(self):
        """ For use with dictionary """
        return hash(self.vertices) 	# since

    def __eq__(self, other):
        """ For use with dictionary """
        assert type(self) == type(other), "Supernode.__eq__: Trying to compare two different types"
        return self.vertices == other.vertices	 # they must be sorted

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self):
        return "Supernode"+self.name
