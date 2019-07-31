""" by Tim Nguyen
    Supernodes class: a container type to hold the candidates as well as some special attributes
    for matching --> including equivalent classes !!! """


class Supernode(object):
    """An object to hold equivalent classes and sets of nodes
    for other data structure. Special is that it sorts the equiv_class
    into a tuple for hashing and comparing if we store supernodes in a dictionary/set for example"""

    channels = []  # class attribute: a list of channels. Initialized in main

    def __init__(self, equiv_class: list or set or tuple, name: str = None):
        """ Note that equiv_class should be either a set, list or tuple
        We use a sorted tuple for hashing and comparing """
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
        return hash(self.vertices)  # since

    def __eq__(self, other):
        """ For use with dictionary """
        assert type(self) == type(other), "Supernode.__eq__: Trying to compare two different types"
        return self.vertices == other.vertices  # they must be sorted

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self):
        return "Supernode" + self.name


class SuperTemplateNode(Supernode):
    """ A class to contain information about the super template nodes
    Each node is an equivalent class and contains additional information
    about clique and connectivity """

    def __init__(
            self, equiv_class: set or tuple or int,
            clique_dict: {str: bool} = None, name: str = None, root=None):
        Supernode.__init__(self, equiv_class, name)
        # a dictionary of channel and a number specifying clique: 0 if not a clique
        # 	otherwise a number to indicate the number of edges that form the clique
        #   IMPORTANT: clique_dict will be of type None if the equiv class is trivial
        self.clique_dict = clique_dict
        self._root = root

    def is_clique(self, channel) -> bool:
        """ Returns whether this supernode is a clique or not (only relevant for size >1)
        """
        if self.is_trivial():  # a single node always forms a clique
            return True
        # the check above ensure the access below is valid
        return self.clique_dict[channel] > 0

    def get_root(self) -> int:
        """ This method is for obtaining one node in the supernode
        Since everything is sorted, this method will always return the same value for the same supernode
        and different values for different supernode in the same problem"""
        return self._root

    def get_size(self) -> int:
        """ Same as len but maybe easier to understand """
        return len(self)

    def is_trivial(self) -> bool:
        """ Returns whether if self is trivial i.e. equiv class of length 1"""
        return len(self) == 1  # is equivalent to checking self.clique_dict is None

    def __str__(self):
        return f"SuperTemplateNode{self.name}"

    def __repr__(self):
        return f"SuperTemplateNode{self.vertices} with cliques: {str(self.clique_dict)}"
