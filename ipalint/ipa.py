from collections import namedtuple

import csv
import logging
import os.path
import unicodedata



"""
Path to the IPA data file.
"""
IPA_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data/ipa.tsv')



"""
Represents a recognised IPA symbol. Its attributes are the character and its
Unicode and IPA names.
"""
Symbol = namedtuple('Symbol', ['char', 'name', 'ipa_name'])



"""
Represents an unrecognised symbol. Its attributes are the character and its
Unicode name.
"""
UnknownSymbol = namedtuple('UnknownSymbol', ['char', 'name'])



class IPADataError(ValueError):
	"""
	Raised when there is a problem with the IPA data file.
	"""
	pass



class Tokeniser:
	"""
	Knows how to the tokenise transcription strings into sequences of Symbol
	named tuples.
	"""
	
	def __init__(self, reporter):
		"""
		Constructor. Expects a Reporter instance to add the lint issues to.
		Raises IPADataError if the IPA data cannot be loaded.
		"""
		self.log = logging.getLogger(__name__)
		self.rep = reporter
		
		self.ipa = self._load_ipa_data(IPA_DATA_PATH)
	
	
	def _load_ipa_data(self, ipa_data_path):
		"""
		Loads and returns the {symbol: name} dictionary stored in the
		data/ipa.tsv file.
		"""
		ipa = {}
		
		try:
			with open(ipa_data_path, newline='') as f:
				reader = csv.reader(f, delimiter='\t')
				for line in reader:
					if len(line) != 2:
						continue
					
					if line[0] in ipa:
						raise IPADataError('')
					
					ipa[line[0]] = line[1]
		
		except (IOError, ValueError) as err:
			self.log.error(str(err))
			raise IPADataError('Could not open the IPA data file')
		
		return ipa
	
	
	def tokenise(self, string):
		"""
		Splits the given string into (1) a tuple of Symbol named tuples; (2) a
		tuple of unknown symbols.
		"""
		symbols = []
		unknown = []
		
		for char in string:
			try:
				name = unicodedata.name(char)
			except ValueError:
				name = 'UNNAMED CHARACTER {}'.format(ord(char))
			
			if char in self.ipa:
				symbols.append(Symbol(char, name, self.ipa[char]))
			else:
				unknown.append(UnknownSymbol(char, name))
		
		return tuple(symbols), tuple(unknown)



