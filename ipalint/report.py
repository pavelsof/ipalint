from collections import namedtuple

import logging



"""
Represents an IPA error found by any of the linters. The lines are the
offending lines in the dataset and the string is the error message.
"""
Error = namedtuple('Error', ['lines', 'string'])



class Reporter:
	"""
	An instance of this class is used to collect all the errors found by the
	various linters, so that they can be output together at the end.
	"""
	
	def __init__(self):
		"""
		Constructor.
		"""
		self.log = logging.getLogger(__name__)
		self.errors = []
	
	
	def add(self, lines, message):
		"""
		"""
		self.errors.append(Error(lines, message))
	
	
	def __str__(self):
		"""
		Returns the string describing all the errors collected so far.
		"""
		return '\n'.join([
			'({}) {}'.format(index, error)
			for index, error in enumerate(self.errors)])


