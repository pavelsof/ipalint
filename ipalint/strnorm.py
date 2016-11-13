import functools
import logging
import unicodedata



class Normaliser:
	"""
	Normalises strings and keeps track of those that (1) do not comply to
	Unicode's normal form; (2) have whitespace issues.
	"""
	
	def __init__(self, nfc_chars=[]):
		"""
		Constructor. The optional arg specifies the set of chars that should
		not be decomposed.
		"""
		self.log = logging.getLogger(__name__)
		
		self.norm_f = functools.partial(unicodedata.normalize, 'NFD')
		
		self.nfc_chars = set(nfc_chars)
		
		self.strip_errors = []
		self.norm_errors = []
	
	
	def normalise(self, string, line_num):
		"""
		Strips the whitespace and applies Unicode normalisation to the given
		string. The second arg is used as an ID of the string when reporting
		its lint errors (if such).
		"""
		stripped = string.strip()
		if stripped != string:
			self.strip_errors.append(line_num)
		
		nfc_pos = [index
					for index, char in enumerate(stripped)
					if char in self.nfc_chars]
		
		parts = []
		start_pos = 0
		
		for pos in nfc_pos:
			if pos > 0:
				parts.append(self.norm_f(stripped[start_pos:pos]))
			
			parts.append(stripped[pos])
			start_pos = pos + 1
		
		if start_pos < len(stripped):
			parts.append(self.norm_f(stripped[start_pos:]))
		
		norm = ''.join(parts)
		
		if norm != stripped:
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


