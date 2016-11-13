from collections import defaultdict, namedtuple

import csv
import logging
import os.path
import unicodedata



"""
Path to the dir in which the data files used by the Recogniser are located.
"""
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


"""
Path to the IPA data file, storing a list of all valid IPA symbols and their
IPA names.
"""
IPA_DATA_PATH = os.path.join(DATA_DIR, 'ipa.tsv')


"""
Path to the common IPA errors data file, storing a mapping of some non-IPA
symbols and their IPA counterparts.
"""
COMMON_ERR_DATA_PATH = os.path.join(DATA_DIR, 'common_errors.tsv')



"""
The only non-IPA character allowed in an IPA string. Any other whitespace
character will be reported as unknown symbols.
"""
SPACE = ' '



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



class Recogniser:
	"""
	Knows how to recognise IPA symbols from non-IPA ones and keeps track of all
	the encountered symbols.
	"""
	
	def __init__(self):
		"""
		Constructor. Raises IPADataError if the IPA data cannot be loaded.
		"""
		self.log = logging.getLogger(__name__)
		
		self.ipa = self._load_ipa_data(IPA_DATA_PATH)
		self.common_err = self._load_common_err_data(COMMON_ERR_DATA_PATH)
		
		self.ipa_symbols = defaultdict(list)  # Symbol: [] of line_num
		self.unk_symbols = defaultdict(list)  # UnknownSymbol: [] of line_num
	
	
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
						raise IPADataError('Bad IPA data file')
					
					ipa[line[0]] = line[1]
		
		except (IOError, ValueError) as err:
			self.log.error(str(err))
			raise IPADataError('Could not open the IPA data file')
		
		return ipa
	
	
	def _load_common_err_data(self, common_err_data_path):
		"""
		Loads and returns the {bad: good} dictionary stored in the common
		errors data file. Note that the dict's keys are single characters while
		the values do not have to be. The method also asserts that all the
		values are valid IPA strings.
		"""
		common_err = {}
		
		try:
			with open(common_err_data_path, newline='') as f:
				reader = csv.reader(f, delimiter='\t')
				for line in reader:
					if len(line) != 2:
						continue
					
					try:
						assert line[0] not in common_err
						assert all([char in self.ipa for char in line[1]])
					except AssertionError:
						raise IPADataError('Bad common IPA errors file')
					
					common_err[line[0]] = line[1]
		
		except (IOError, ValueError) as err:
			self.log.error(str(err))
			raise IPADataError('Could not open the common IPA errors data file')
		
		return common_err
	
	
	def get_nfc_chars(self):
		"""
		Returns the set of IPA symbols that are precomposed (decomposable)
		chars. These should not be decomposed during string normalisation,
		because they will not be recognised otherwise.
		
		In IPA 2015 there is only one precomposed character: ç, the voiceless
		palatal fricative.
		"""
		ex = []
		
		for char in self.ipa.keys():
			if len(char) == 1:
				decomp = unicodedata.normalize('NFD', char)
				if len(decomp) == 2:
					ex.append(char)
		
		return set(ex)
	
	
	def recognise(self, string, line_num):
		"""
		Splits the string into chars and distributes these into the buckets of
		IPA and non-IPA symbols. Expects that there are no precomposed chars in
		the string.
		"""
		symbols = []
		unknown = []
		
		for char in string:
			if char == SPACE:
				continue
			
			try:
				name = unicodedata.name(char)
			except ValueError:
				name = 'UNNAMED CHARACTER {}'.format(ord(char))
			
			if char in self.ipa:
				symbol = Symbol(char, name, self.ipa[char])
				symbols.append(symbol)
				self.ipa_symbols[symbol].append(line_num)
			else:
				symbol = UnknownSymbol(char, name)
				unknown.append(symbol)
				self.unk_symbols[symbol].append(line_num)
		
		return tuple(symbols), tuple(unknown)
	
	
	def report(self, reporter):
		"""
		Adds the problems that have been found so far to the given Reporter
		instance.
		"""
		for symbol in sorted(self.unk_symbols.keys()):
			err = '{} ({}) is not part of IPA'.format(symbol.char, symbol.name)
			
			if symbol.char in self.common_err:
				repl = self.common_err[symbol.char]
				err += ', suggested replacement is {}'.format(repl)
				if len(repl) == 1:
					err += ' ({})'.format(unicodedata.name(repl))
			
			reporter.add(self.unk_symbols[symbol], err)


