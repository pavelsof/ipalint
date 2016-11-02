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



class DatabaseError(ValueError):
	"""
	Raised when there is a problem with the IPA data file.
	"""
	pass



class Database:
	"""
	Knows how to the segmentise transcription strings into sequences of Segment
	named tuples.
	"""
	
	def __init__(self, load=False):
		"""
		Constructor.
		"""
		self.log = logging.getLogger(__name__)
		self.ipa = self._load_ipa(IPA_DATA_PATH)
	
	
	def _load_ipa(self, ipa_data_path):
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
						raise DatabaseError('')
					
					ipa[line[0]] = line[1]
		
		except (IOError, ValueError) as err:
			self.log.error(str(err))
			raise DatabaseError('Could not open the IPA data file')
		
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



