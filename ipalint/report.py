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
	
	
	def clear(self):
		"""
		Removes the errors that have been collected so far. Useful for unit
		testing.
		"""
		self.errors = OrderedDict()
	
	
	def _get_linewise_report(self):
		"""
		Returns a report each line of which comprises a pair of an input line
		and an error. Unlike in the standard report, errors will appear as many
		times as they occur.
		
		Helper for the get_report method.
		"""
		d = defaultdict(list)  # line: [] of errors
		
		for error, lines in self.errors.items():
			for line_num in lines:
				d[line_num].append(error)
		
		return '\n'.join([
			'{:>3} → {}'.format(line, error.string)
			for line in sorted(d.keys())
			for error in d[line]])
	
	
	def _get_report(self, with_line_nums=True):
		"""
		Returns a report which includes each distinct error only once, together
		with a list of the input lines where the error occurs. The latter will
		be omitted if flag is set to False.
		
		Helper for the get_report method.
		"""
		templ = '{} ← {}' if with_line_nums else '{}'
		
		return '\n'.join([
			templ.format(error.string, ','.join(map(str, sorted(set(lines)))))
			for error, lines in self.errors.items()])
	
	
	def get_report(self, linewise=False, no_lines=False):
		"""
		Returns a string describing all the errors collected so far (the
		report). The first flag determines the type of report. The second flag
		is ignored if the first is set to True.
		"""
		if linewise:
			return self._get_linewise_report()
		else:
			return self._get_report(not no_lines)


