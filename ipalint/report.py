from collections import defaultdict, namedtuple, OrderedDict

import logging



"""
Represents an IPA error found by any of the linters.
"""
Error = namedtuple('Error', ['string'])



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
		self.errors = OrderedDict()  # error: [] of line numbers
	
	
	def add(self, lines, message):
		"""
		Adds a lint issue to the report. The first arg should be [] of lines on
		which the issue is present. The second arg should be the error message.
		"""
		error = Error(message)
		
		if error not in self.errors:
			self.errors[error] = []
		
		self.errors[error].extend(lines)
	
	
	def _get_linewise_report(self):
		d = defaultdict(list)  # line: [] of errors
		
		for error, lines in self.errors.items():
			for line_num in lines:
				d[line_num].append(error)
		
		return '\n'.join([
			'{} → {}'.format(line, error.string)
			for line, errors in d.items()
			for error in errors])
	
	
	def get_report(self, linewise=False, ignores=[]):
		"""
		Returns the string describing all the errors collected so far.
		"""
		if linewise:
			return self._get_linewise_report()
		
		else:
			return '\n'.join([
				'{} → {}'.format(error.string, ','.join(map(str, lines)))
				for error, lines in self.errors.items()])


