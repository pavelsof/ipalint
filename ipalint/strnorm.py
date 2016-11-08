import logging
import unicodedata



class Normaliser:
	"""
	Normalises strings and keeps track of those that (1) do not comply to
	Unicode's normal form; (2) have whitespace issues.
	"""
	
	def __init__(self):
		"""
		Constructor. Inits the lists that keep track of the offending strings.
		"""
		self.log = logging.getLogger(__name__)
		
		self.strip_errors = []
		self.norm_errors = []
	
	
	def normalise(self, string, line_num):
		"""
		Applies Unicode normalisation to the given string and collapses the
		whitespace.
		"""
		stripped = string.strip()
		if stripped != string:
			self.strip_errors.append(line_num)
		
		norm = unicodedata.normalize('NFD', stripped)
		
		if norm != string:
			self.norm_errors.append(line_num)
		
		return norm
	
	
	def report(self, reporter, ignore_nfd=False, ignore_ws=False):
		"""
		Adds the problems that have been found so far to the given Reporter
		instance. The two keyword args can be used to restrict the error types
		to be reported.
		"""
		if self.strip_errors and not ignore_ws:
			reporter.add(self.strip_errors, 'leading or trailing whitespace')
		
		if self.norm_errors and not ignore_nfd:
			reporter.add(self.norm_errors, 'not in Unicode NFD')


