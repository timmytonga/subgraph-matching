""" by Tim Nguyen
Supernodes class: a container type to hold the candidates as well as some special attributes
	for matching --> including equivalent classes !!! """


class Supernode(object):
	"""Contains information about supernodes such as candidates and """

	def __init__(self, equiv_class: 'templt nodes'):
		self.vertices 	= tuple(sorted(equiv_class)) # for ease of comparing
		self.size 		= len(self.vertices)

	def get_vertices(self) -> tuple:
		""" returns a tuple of vertices of the equiv class of the supernode"""
		return self.vertices

	def __len__(self):
		""" Returns the number of template node it contains """
		return self.size

	def __hash__(self):
		""" For use with dictionary """
		return hash(self.vertices) 	# since

	def __eq__(self, other):
		""" For use with dictionary """
		assert type(self) == type(other), "Trying to compare two different types"
		return self.vertices == other.vertices	 # they must be sorted

	def __ne__(self, other) -> bool:
		return not self.__eq__(other)

	def __str__(self):
		return str(self.vertices)

