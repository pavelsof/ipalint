import csv
import os.path
import string

from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis.strategies import fixed_dictionaries, integers
from hypothesis.strategies import lists, sampled_from, text
from hypothesis import assume, given

from ipalint.read import IPA_COL_NAMES, Reader



FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

HAWAIIAN_TSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.tsv')
HAWAIIAN_CSV_PATH = os.path.join(FIXTURES_DIR, 'hawaiian.csv')



class ReaderTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
	
	
	def tearDown(self):
		self.temp_dir.cleanup()
	
	
	@given(sampled_from(IPA_COL_NAMES), lists(text()))
	def test_infer_ipa_col(self, col_name, li):
		assume(all([i not in IPA_COL_NAMES for i in li]))
		reader = Reader(None)
		
		for pos in range(len(li)+1):
			header = list(li)
			header.insert(pos, col_name)
			self.assertEqual(reader._infer_ipa_col(header), pos)
		
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(lists(sampled_from(IPA_COL_NAMES), min_size=2))
	def test_infer_ipa_col_error(self, li):
		reader = Reader(None)
		with self.assertRaises(ValueError):
			reader._infer_ipa_col(li)
	
	
	@given(integers(min_value=1, max_value=42).flatmap(lambda n: fixed_dictionaries({
			'lines': lists(lists(text(min_size=1, alphabet=string.printable),
								min_size=n, max_size=n), min_size=1),
			'col': integers(min_value=0, max_value=n-1)})))
	def test_gen_ipa_data(self, d):
		file_path = os.path.join(self.temp_dir.name, 'test')
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			for line in d['lines']: writer.writerow(line)
		
		data = [line[d['col']] for line in d['lines']]
		res = []
		
		reader = Reader(file_path, has_header=False, ipa_col=d['col'])
		for datum in reader.gen_ipa_data():
			res.append(datum)
		
		self.assertEqual(res, data)
	
	
	def test_gen_ipa_data_hawaiian(self):
		reader = Reader(HAWAIIAN_TSV_PATH, ipa_col=3)
		data = [datum for datum in reader.gen_ipa_data()]
		self.assertEqual(len(data), 246)
		
		self.assertEqual(data[0], 'lima')
		self.assertEqual(data[209], '[\'o] au')
		self.assertEqual(data[245], 'kaukani')
		
		# reader2 = Reader(HAWAIIAN_CSV_PATH, ipa_col=3)
		# data2 = [datum for datum in reader2.gen_ipa_data()]
		# self.assertEqual(data, data2)
	
	
	def test_gen_ipa_data_error(self):
		file_path = os.path.join(self.temp_dir.name, 'test')
		
		with open(file_path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(['a', 'b', 'c'])
		
		reader = Reader(file_path, has_header=False, ipa_col=3)
		
		with self.assertRaises(ValueError):
			[datum for datum in reader.gen_ipa_data()]


