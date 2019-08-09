""" Simple utilities used for debugging, logging, profiling, testing, etc. """

import datetime
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('root')
solution_logger = logging.getLogger('solution')
DEBUG = True  # set this flag True to toggle DEBUG
VERBOSE = True  # set the flag to True for verbose
NAME = f"[{str(datetime.datetime.now().strftime('%Y-%m-%d'))}] NoName"


def init_logger(log_level=logging.INFO):
	# setup logger
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	LOGFILE_NAME = '{}.log'.format(NAME)  # TODO: Set this to correct format when logging
	fh = RotatingFileHandler(LOGFILE_NAME, mode='w', maxBytes=500 * 1024 * 1024, backupCount=10, encoding=None, delay=0)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	logger.setLevel(log_level)

	solfh = logging.FileHandler(f"{NAME}.sol")
	solfh.setFormatter(formatter)
	solution_logger.setLevel(logging.INFO)
	solution_logger.addHandler(solfh)


class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def set_name(name):
	global NAME
	NAME = name


def get_now():
	""" Get a str of current time"""
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ## Trivial utils
def print_debug(msg, end="\n"):
	""" Logging and stuff """
	if DEBUG:
		logger.debug(msg)
		print(f"{bcolors.WARNING}DEBUG:{bcolors.ENDC}", msg, end=end)


def print_info(msg: str, end="\n"):
	logger.info(msg)
	if VERBOSE:
		print(f"{bcolors.BOLD}UPDATE:{bcolors.ENDC}", msg, end=end)


def print_warning(msg: str, end="\n"):
	logger.warning(msg)
	if VERBOSE:
		print(f"{bcolors.FAIL}WARNING:{bcolors.ENDC}", msg, end=end)


def get_dict_str(d: dict) -> str:
	""" Given a dictionary, give a str output of key and value """
	return str({str(u): str(v) for u, v in d.items()})


def get_itr_str(iterable) -> str:
	""" Given a list, set or tuple returns str of values """
	return str([str(i) for i in iterable])


def log_solutions(msg: str):
	solution_logger.info(msg)


def print_stats(partition, graph, detailed=True, name=False):
	equiv_classes = partition.classes()
	# compute some stats
	print("==== GENERAL-STATS =====")
	# the number of nodes
	print("Total number of original nodes: " + str(len(partition)))
	# the number of equiv classes
	print("Total number of equiv classes: " + str(len(equiv_classes)))
	# compression percentage
	compression_percentage = 1 - len(equiv_classes) / len(partition)
	print("Compression percentage (1 - equiv_classes/total_number_of_nodes): %4.2f" % (compression_percentage))
	equiv_classes = partition.classes()
	equiv_classes_name = []
	for s in equiv_classes:
		equiv_classes_name.append({graph.nodes[i] for i in s})
	if detailed:
		print("===== EQUIVALENCE CLASSES ===== ")
		if name:
			print(equiv_classes_name)
		else:
			print(equiv_classes)

	print("===== NON-TRIVIAL EQUIV CLASSES ===== ")
	non_triv = [i for i in equiv_classes if len(i) > 1]
	non_triv_name = []
	for s in non_triv:
		non_triv_name.append({graph.nodes[i] for i in s})
	if detailed:
		if name:
			print(non_triv_name)
		else:
			print(non_triv)
	print("Number of non-trivial equiv classes: %d" % len(non_triv))

	sizes = [len(l) for l in non_triv]
	if detailed:
		print("Sizes of equiv classes: " + str(sizes))
		print("Largest equiv size: %d" % (max(sizes)))


def compute_non_trivial(adj_matrix):
	result = []
	for i in range(adj_matrix.shape[0]):
		if adj_matrix[i].any() or adj_matrix[:, i].any():
			result.append(i)
	return result
