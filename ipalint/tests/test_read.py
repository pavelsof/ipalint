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

HAWAIIAN_TSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.tsv')
HAWAIIAN_CSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.csv')



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
	
	
	def test_sniff(self):
		reader = Reader(HAWAIIAN_CSV_PATH)
		dialect = reader.sniff()
		self.assertEqual(dialect.delimiter, ',')
		self.assertEqual(dialect.doublequote, True)
		self.assertEqual(dialect.quotechar, '"')
		self.assertEqual(dialect.skipinitialspace, False)
		
		reader = Reader(HAWAIIAN_TSV_PATH)
		dialect = reader.sniff()
		self.assertEqual(dialect.delimiter, '\t')
		self.assertEqual(dialect.doublequote, True)
		self.assertEqual(dialect.skipinitialspace, False)
	
	
	@given(list_and_index(text(min_size=1)))
	def test_infer_ipa_col_index(self, lind):
		li, index = lind
		assume(all([not t.isnumeric() for t in li]))
		
		reader = Reader(None, ipa_col=str(index))
		self.assertEqual(reader._infer_ipa_col(li), index)
	
	
	@given(list_and_index(text(min_size=1)))
	def test_infer_ipa_col_name(self, lind):
		li, index = lind
		reader = Reader(None, ipa_col=li[index])
		self.assertEqual(reader._infer_ipa_col(li), index)
	
	
	@given(lists(text(min_size=1)), not_int_text())
	def test_infer_ipa_col_name_error(self, li, t):
		assume(t not in li)
		
		reader = Reader(None, ipa_col=t)
		
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(sampled_from(IPA_COL_NAMES), lists(text()))
	def test_infer_ipa_col_guess(self, col_name, li):
		assume(all([i not in IPA_COL_NAMES for i in li]))
		reader = Reader(None)
		
		for pos in range(len(li)+1):
			header = list(li)
			header.insert(pos, col_name)
			self.assertEqual(reader._infer_ipa_col(header), pos)
		
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(lists(sampled_from(IPA_COL_NAMES), min_size=2))
	def test_infer_ipa_col_guess_error(self, li):
		reader = Reader(None)
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
		
		reader2 = Reader(HAWAIIAN_TSV_PATH, ipa_col=3)
		data2 = [res for res in reader2.gen_ipa_data()]
		self.assertEqual(data, data2)
	
	
	def test_gen_ipa_data_error(self):
		file_path = os.path.join(self.temp_dir.name, 'test')
		
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(['a', 'b', 'c'])
		
		reader = Reader(file_path, has_header=False, ipa_col=3)
		
		with self.assertRaises(ValueError):
			[res for res in reader.gen_ipa_data()]


