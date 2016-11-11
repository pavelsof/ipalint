"""
This module provides the code for reading the datasets which are to be linted.
"""

import csv
import logging
import os.path



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
List of lower-cased prefixes of common names for the column that contains the
IPA data.
"""
IPA_COL_NAMES = ['ipa', 'phon', 'transcription']



class Reader:
	"""
	Knows how to read arbitrary csv/tsv datasets (or at least as arbitrary as
	csv.Sniffer can recognise).
	"""
	
	def __init__(self, file_path, has_header=True, ipa_col=None):
		"""
		Constructor. Expects the path to the file to be read. Optional args:
		
		has_header: whether the first line of the file will be ignored or not;
		ipa_col: the column from which to extract the IPA data; this could be
		either the column's index or name, or None (in which case the Reader
		will try to guess the column).
		"""
		self.log = logging.getLogger(__name__)
		
		self.file_path = file_path
		
		self.has_header = has_header
		self.ipa_col = ipa_col
		
		self.dialect = None
	
	
	def _open(self, file_path=None):
		"""
		Opens the file specified by the given path. Raises ValueError if there
		is a problem with opening or reading the file.
		"""
		if not file_path:
			file_path = self.file_path
		
		if not os.path.exists(file_path):
			raise ValueError('Could not find file: {}'.format(file_path))
		
		try:
			f = open(file_path, encoding='utf-8', newline='')
		except OSError as err:
			self.log.error(str(err))
			raise ValueError('Could not open file: {}'.format(file_path))
		
		return f
	
	
	def sniff(self):
		"""
		Opens the dataset and tries to infer whether the format is csv, tsv, or
		simply a single column of IPA data. Raises ValueError if unsuccessful.
		
		In most scenarios, this will be the first time when the file is opened,
		which can also raises a ValueError.
		"""
		ext = os.path.basename(self.file_path).rsplit('.', maxsplit=1)
		ext = ext[1].lower() if len(ext) > 1 else None
		
		delimiters = '\t' if ext in ['tsv', 'tab'] else ',\t;:'
		
		f = self._open()
		
		try:
			self.dialect = csv.Sniffer().sniff(f.read(), delimiters=delimiters)
		except csv.Error as err:
			self.log.error(str(err))
			raise ValueError('Could not determine csv dialect')
		finally:
			f.close()
		
		if ext in ['tsv', 'tab']:
			self.dialect.quotechar = '"'
		
		return self.dialect
	
	
	def _determine_dialect(self, lines):
		"""
		Expects a non-empty [] of strings; that would normally be the first few
		lines of a csv file. Returns the most likely delimiter, quotechar tuple
		or None if the data seems to form a single column.
		
		Ensures that using the returned delimiter and quotechar, all the lines
		given will have the same number of columns.
		"""
		for delim in CSV_DELIMITERS:
			counts = [line.count(delim) for line in lines]
			
			if min(counts) == 0:
				continue
			
			for quotechar in CSV_QUOTECHARS:
				reader = csv.reader(lines, delimiter=delim, quotechar=quotechar)
				
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
		
		return delim, quotechar
	
	
	def _get_reader(self, f):
		"""
		Returns a csv.reader for the given file handler. If the file has a
		header, it already will be gone through.
		
		Also, if self.ipa_col is not set, an attempt will be made to infer
		which the IPA column is. ValueError would be raised otherwise.
		"""
		if not self.dialect:
			self.sniff()
		
		reader = csv.reader(f, dialect=self.dialect)
		
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
		Generator for iterating over the IPA strings found in the file. Yields
		the IPA data string paired with the respective line number.
		"""
		f = self._open()
		
		try:
			reader = self._get_reader(f)
			
			for line in reader:
				try:
					datum = line[self.ipa_col]
				except IndexError:
					mes = 'Could not find IPA data on line: {}'.format(line)
					raise ValueError(mes)
				
				yield datum, reader.line_num
		
		finally:
			f.close()


