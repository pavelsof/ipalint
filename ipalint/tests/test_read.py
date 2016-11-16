import csv
import os.path
import string

from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis.strategies import composite, fixed_dictionaries, integers
from hypothesis.strategies import lists, sampled_from, sets, text
from hypothesis import assume, given

from ipalint.read import IPA_COL_NAMES, Reader



FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

HAWAIIAN_CSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.csv')
HAWAIIAN_TSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.tsv')
HAWAIIAN_TXT_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.txt')



CHARS_EXCL_NEWLINES = string.printable.rstrip('\r\n\x0b\x0c')



@composite
def list_and_index(draw, elements):
	li = list(draw(sets(elements, min_size=1)))
	index = draw(integers(min_value=0, max_value=len(li)-1))
	return li, index



@composite
def not_int_text(draw):
	t = draw(text())
	try:
		int(t)
	except ValueError:
		return t
	else:
		assume(False)



class ReaderTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
	
	
	def tearDown(self):
		self.temp_dir.cleanup()
	
	
	def test_save_stdin(self):
		with open(HAWAIIAN_TSV_PATH) as f:
			reader = Reader(f)
		
		with open(HAWAIIAN_TSV_PATH) as f:
			lines = f.read()
		
		with open(reader.file_path) as f:
			temp_lines = f.read()
		
		self.assertEqual(lines, temp_lines)
	
	
	def test_save_stdin_error(self):
		for item in [None, True, False, 42]:
			with self.assertRaises(ValueError):
				Reader(None)
	
	
	def test_get_dialect(self):
		reader = Reader(HAWAIIAN_CSV_PATH)
		dialect = reader.get_dialect()
		self.assertEqual(dialect.delimiter, ',')
		self.assertEqual(dialect.quotechar, '"')
		self.assertEqual(dialect.doublequote, False)
		self.assertEqual(dialect.escapechar, '\\')
		
		reader = Reader(HAWAIIAN_TSV_PATH)
		dialect = reader.get_dialect()
		self.assertEqual(dialect.delimiter, '\t')
		self.assertEqual(dialect.quotechar, '"')
		self.assertEqual(dialect.doublequote, True)
		self.assertEqual(dialect.escapechar, None)
		
		reader = Reader(HAWAIIAN_TXT_PATH)
		dialect = reader.get_dialect()
		self.assertEqual(dialect, None)
	
	
	def test_determine_dialect(self):
		reader = Reader('')
		
		with open(HAWAIIAN_CSV_PATH, newline='') as f:
			lines = f.read().splitlines()
		
		dialect = reader._determine_dialect(lines)
		self.assertEqual(dialect.delimiter, ',')
		self.assertEqual(dialect.quotechar, '"')
		self.assertEqual(dialect.doublequote, False)
		self.assertEqual(dialect.escapechar, '\\')
		
		with open(HAWAIIAN_TSV_PATH, newline='') as f:
			lines = f.read().splitlines()
		
		dialect = reader._determine_dialect(lines)
		self.assertEqual(dialect.delimiter, '\t')
		self.assertEqual(dialect.quotechar, '"')
		self.assertEqual(dialect.doublequote, True)
		self.assertEqual(dialect.escapechar, None)
	
	
	@given(integers(min_value=2, max_value=20).flatmap(lambda cols:
				lists(lists(text(alphabet=CHARS_EXCL_NEWLINES),
						min_size=cols, max_size=cols), min_size=1)))
	def test_determine_dialect_comma(self, data):
		file_path = os.path.join(self.temp_dir.name, 'test')
		reader = Reader(file_path)
		
		for dialect in [csv.excel, csv.unix_dialect]:
			with open(file_path, 'w', newline='') as f:
				writer = csv.writer(f, dialect=dialect)
				for line in data:
					writer.writerow(line)
			
			with open(file_path, newline='') as f:
				lines = f.read().splitlines()
			
			res = reader._determine_dialect(lines)
			self.assertEqual(res.delimiter, ',')
			self.assertEqual(res.quotechar, '"')
			self.assertEqual(res.doublequote, True)
			self.assertEqual(res.escapechar, None)
	
	
	@given(integers(min_value=2, max_value=20).flatmap(lambda cols:
				lists(lists(text(alphabet=CHARS_EXCL_NEWLINES.rstrip('\t')),
						min_size=cols, max_size=cols), min_size=10)))
	def test_determine_dialect_tab(self, data):
		file_path = os.path.join(self.temp_dir.name, 'test')
		reader = Reader(file_path)
		
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f, dialect=csv.excel_tab)
			for line in data:
				writer.writerow(line)
		
		with open(file_path, newline='') as f:
			lines = f.read().splitlines()
		
		res = reader._determine_dialect(lines)
		self.assertEqual(res.delimiter, '\t')
		self.assertEqual(res.quotechar, '"')
		self.assertEqual(res.doublequote, True)
		self.assertEqual(res.escapechar, None)
	
	
	@given(list_and_index(text(min_size=1)))
	def test_infer_ipa_col_index(self, lind):
		li, index = lind
		assume(all([not t.isnumeric() for t in li]))
		
		reader = Reader('', ipa_col=str(index))
		self.assertEqual(reader._infer_ipa_col(li), index)
	
	
	@given(list_and_index(text(min_size=1)))
	def test_infer_ipa_col_name(self, lind):
		li, index = lind
		reader = Reader('', ipa_col=li[index])
		self.assertEqual(reader._infer_ipa_col(li), index)
	
	
	@given(lists(text(min_size=1)), not_int_text())
	def test_infer_ipa_col_name_error(self, li, t):
		assume(t not in li)
		
		reader = Reader('', ipa_col=t)
		
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(sampled_from(IPA_COL_NAMES), lists(text()))
	def test_infer_ipa_col_guess(self, col_name, li):
		assume(all([i not in IPA_COL_NAMES for i in li]))
		reader = Reader('')
		
		for pos in range(len(li)+1):
			header = list(li)
			header.insert(pos, col_name)
			self.assertEqual(reader._infer_ipa_col(header), pos)
		
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(lists(sampled_from(IPA_COL_NAMES), min_size=2))
	def test_infer_ipa_col_guess_error(self, li):
		reader = Reader('')
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(integers(min_value=2, max_value=42).flatmap(lambda n: fixed_dictionaries({
			'lines': lists(lists(text(min_size=1, alphabet=string.ascii_letters),
								min_size=n, max_size=n), min_size=2),
			'col': integers(min_value=0, max_value=n-1)})))
	def test_gen_ipa_data(self, d):
		file_path = os.path.join(self.temp_dir.name, 'test')
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f)
			for line in d['lines']: writer.writerow(line)
		
		data = [line[d['col']] for line in d['lines']]
		res = []
		
		reader = Reader(file_path, has_header=False, ipa_col=d['col'])
		for datum, line_num in reader.gen_ipa_data():
			res.append(datum)
		
		self.assertEqual(res, data)
	
	
	def test_gen_ipa_data_hawaiian(self):
		reader = Reader(HAWAIIAN_CSV_PATH, ipa_col=3)
		data = [datum for datum in reader.gen_ipa_data()]
		self.assertEqual(len(data), 246)
		
		self.assertEqual(data[0], ('lima', 2))
		self.assertEqual(data[209], ('[\'o] au', 211))
		self.assertEqual(data[245], ('kaukani', 247))
		
		reader_tsv = Reader(HAWAIIAN_TSV_PATH, ipa_col=3)
		data_tsv = [res for res in reader_tsv.gen_ipa_data()]
		self.assertEqual(data_tsv, data)
		
		reader_txt = Reader(HAWAIIAN_TXT_PATH)
		data_txt = [res for res in reader_txt.gen_ipa_data()]
		self.assertEqual(data_txt, data)
	
	
	def test_gen_ipa_data_empty(self):
		reader = Reader([])
		data = [datum for datum in reader.gen_ipa_data()]
		self.assertEqual(len(data), 0)
	
	
	def test_gen_ipa_data_error(self):
		file_path = os.path.join(self.temp_dir.name, 'test')
		
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(['a', 'b', 'c'])
		
		reader = Reader(file_path, has_header=False, ipa_col=3)
		
		with self.assertRaises(ValueError):
			[res for res in reader.gen_ipa_data()]


