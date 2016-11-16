from collections import namedtuple

import csv
import logging
import os.path

from tempfile import TemporaryDirectory



"""
List of possible csv delimiters; when trying to determine the delimtier of a
csv file, these will be tried in the order given here.
"""
CSV_DELIMITERS = [',', '\t', ';', ':', '|']



"""
List of possible csv quotechars that will be tried (in the order given here)
when trying to determine the quotechar of a csv file.
"""
CSV_QUOTECHARS = ['"', "'"]



"""
List of possible csv escapechars that will be tried when determining the csv
dialect. None means that the escapechar is the same as the quotechar.
"""
CSV_ESCAPECHARS = [None, '\\']



"""
List of file extension that are considered identifying tab-separated values; no
no dialect guessing will take place for these files.
"""
TSV_EXTENSIONS = ['tsv', 'tab']



"""
List of lower-cased prefixes of common names for the column that contains the
IPA data.
"""
IPA_COL_NAMES = ['ipa', 'phon', 'transcription']



"""
Contains the parameters to be fed into the csv.reader that will produce the
lines of the dataset file.
"""
Dialect = namedtuple('Dialect',
		['delimiter', 'quotechar', 'doublequote', 'escapechar'])



class Reader:
	"""
	Comprises the code for reading the dataset file which is to be linted.
	"""
	
	def __init__(self, dataset, has_header=True, ipa_col=None,
						delimiter=None, quotechar=None, escapechar=None):
		"""
		Constructor. Expects either the path to the file to be read or an input
		stream to read from. Optional args:
		
		has_header: whether the first line of the file will be ignored or not;
		ipa_col: the column from which to extract the IPA data; this could be
		either the column's index or name, or None (in which case the Reader
		will try to guess the column);
		delimiter and quotechar: will be used as csv.reader arguments if
		provided; if None, the Reader will try to guess the dialect.
		"""
		self.log = logging.getLogger(__name__)
		self.temp_dir = None
		
		if isinstance(dataset, str):
			self.file_path = dataset
		else:
			self.file_path = self._save_stdin(dataset)
		
		self.has_header = has_header
		self.ipa_col = ipa_col
		
		self.is_single_col = False
		
		self.delimiter = delimiter
		self.quotechar = quotechar
		self.escapechar = escapechar
	
	
	def _save_stdin(self, stdin):
		"""
		Creates a temporary dir (self.temp_dir) and saves the given input
		stream to a file within that dir. Returns the path to the file. The dir
		is removed in the __del__ method.
		"""
		self.temp_dir = TemporaryDirectory()
		file_path = os.path.join(self.temp_dir.name, 'dataset')
		
		try:
			with open(file_path, 'w') as f:
				for line in stdin:
					f.write(line)
		except TypeError:
			self.temp_dir.cleanup()
			raise ValueError('Could not read stdin')
		
		return file_path
	
	
	def _open(self, file_path=None):
		"""
		Opens the file specified by the given path. Raises ValueError if there
		is a problem with opening or reading the file.
		"""
		if file_path is None:
			file_path = self.file_path
		
		if not os.path.exists(file_path):
			raise ValueError('Could not find file: {}'.format(file_path))
		
		try:
			f = open(file_path, encoding='utf-8', newline='')
		except OSError as err:
			self.log.error(str(err))
			raise ValueError('Could not open file: {}'.format(file_path))
		
		return f
	
	
	def get_dialect(self):
		"""
		Returns a Dialect named tuple or None if the dataset file comprises a
		single column of data. If the dialect is not already known, then tries
		to determine it. Raises ValueError if it fails in the latter case.
		"""
		if self.is_single_col:
			return None
		
		if self.delimiter and self.quotechar:
			return Dialect(self.delimiter, self.quotechar,
						True if self.escapechar is None else False,
						self.escapechar)
		
		ext = os.path.basename(self.file_path).rsplit('.', maxsplit=1)
		ext = ext[1].lower() if len(ext) > 1 else None
		
		if ext in TSV_EXTENSIONS:
			self.delimiter = '\t'
			self.quotechar = '"'
		
		else:
			f = self._open()
			lines = f.read().splitlines()
			f.close()
			
			if lines:
				dialect = self._determine_dialect(lines)
			else:
				dialect = None
			
			if dialect is None:
				self.is_single_col = True
			else:
				self.delimiter = dialect.delimiter
				self.quotechar = dialect.quotechar
				self.escapechar = dialect.escapechar
		
		return self.get_dialect()
	
	
	def _determine_dialect(self, lines):
		"""
		Expects a non-empty [] of strings; these would normally be the first
		few lines of a csv file. Returns the most likely Dialect named tuple or
		None if the data seems to form a single column.
		
		Ensures that using the returned dialect, all the lines given will have
		the same number of columns.
		
		Helper for the get_dialect method.
		"""
		permuts = [(quotechar, escapechar)
				for quotechar in CSV_QUOTECHARS
				for escapechar in CSV_ESCAPECHARS]
		
		for delim in CSV_DELIMITERS:
			counts = [line.count(delim) for line in lines]
			
			if min(counts) == 0:
				continue
			
			for quotechar, escapechar in permuts:
				doublequote = True if escapechar is None else False
				
				reader = csv.reader(lines, delimiter=delim, quotechar=quotechar,
								doublequote=doublequote, escapechar=escapechar)
				
				try:
					assert len(set([len(line) for line in reader])) == 1
				except AssertionError:
					continue
				else:
					break
			else:
				continue  # no suitable quoting found
			
			break  # found it!
		
		else:
			return None
		
		return Dialect(delim, quotechar, doublequote, escapechar)
	
	
	def _get_csv_reader(self, f, dialect):
		"""
		Returns a csv.reader for the given file handler and csv Dialect named
		tuple. If the file has a header, it already will be gone through.
		
		Also, if self.ipa_col is not set, an attempt will be made to infer
		which the IPA column is. ValueError would be raised otherwise.
		"""
		reader = csv.reader(f,
					delimiter = dialect.delimiter,
					quotechar = dialect.quotechar,
					doublequote = dialect.doublequote,
					escapechar = dialect.escapechar)
		
		if self.has_header:
			header = next(reader)
			if not isinstance(self.ipa_col, int):
				self.ipa_col = self._infer_ipa_col(header)
		
		else:
			if not isinstance(self.ipa_col, int):
				if not self.ipa_col:
					raise ValueError('Cannot infer IPA column without header')
				
				try:
					self.ipa_col = int(self.ipa_col)
				except ValueError:
					raise ValueError('Cannot find column: {}'.format(self.ipa_col))
		
		return reader
	
	
	def _infer_ipa_col(self, header):
		"""
		Returns the column (as index) containing the IPA data based on the
		header (the first line of the data file). Raises ValueError otherwise.
		
		If self.ipa_col is a string, it is assumed to be the column's name or
		index. Otherwise, several common IPA column names are tried.
		"""
		if self.ipa_col and isinstance(self.ipa_col, str):
			if self.ipa_col in header:
				return header.index(self.ipa_col)
			
			try:
				ipa_col = int(self.ipa_col)
			except ValueError: pass
			else:
				return ipa_col
			
			raise ValueError('Could not find column: {}'.format(self.ipa_col))
		
		pot = []
		
		for index, col_name in enumerate(header):
			col_name = col_name.lower()
			for name in IPA_COL_NAMES:
				if col_name.startswith(name):
					pot.append(index)
		
		if len(pot) == 0:
			raise ValueError('Could not find an IPA column')
		elif len(pot) > 1:
			raise ValueError('Could not decide which is the IPA column')
		
		return pot[0]
	
	
	def gen_ipa_data(self):
		"""
		Generator for iterating over the IPA strings found in the dataset file.
		Yields the IPA data string paired with the respective line number.
		"""
		dialect = self.get_dialect()
		f = self._open()
		
		try:
			if dialect:
				for res in self._gen_csv_data(f, dialect):
					yield res
			else:
				for res in self._gen_txt_data(f):
					yield res
		
		finally:
			f.close()
	
	
	def _gen_csv_data(self, f, dialect):
		"""
		Yields (column data, row number) tuples from the given csv file
		handler, using the given Dialect named tuple instance. Depends on
		self.ipa_col being correctly set.
		
		Helper for the gen_ipa_data method.
		"""
		reader = self._get_csv_reader(f, dialect)
		
		for line in reader:
			try:
				datum = line[self.ipa_col]
			except IndexError:
				mes = 'Could not find IPA data on line: {}'.format(line)
				raise ValueError(mes)
			
			yield datum, reader.line_num
	
	
	def _gen_txt_data(self, f):
		"""
		Yields (line, line number) tuples from the given file handler. Skips
		the first line if the self.has_header flag is set.
		
		Helper for the gen_ipa_data method.
		"""
		reader = iter(f)
		
		for line_num, line in enumerate(reader):
			if line_num == 0 and self.has_header:
				continue
			
			datum = line.rstrip('\r\n')
			
			yield datum, line_num+1
	
	
	def __del__(self):
		"""
		Destructor. Removes the temporary directory, if such.
		"""
		if self.temp_dir:
			self.temp_dir.cleanup()


