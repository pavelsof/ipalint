import csv
import os.path
import string

from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis.strategies import fixed_dictionaries, integers
from hypothesis.strategies import lists, sampled_from, text
from hypothesis import assume, given

from ipalint.read import IPA_COL_NAMES, Reader



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
		for line in reader.gen_ipa_data():
			res.append(line)
		
		self.assertEqual(res, data)


