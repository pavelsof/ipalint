import string

from unittest import TestCase

from hypothesis.strategies import dictionaries, integers
from hypothesis.strategies import lists, text, tuples
from hypothesis import given

from ipalint.report import Reporter



class ReporterTestCase(TestCase):
	
	def setUp(self):
		self.rep = Reporter()
	
	
	@given(dictionaries(text(alphabet=string.ascii_letters, min_size=1),
			lists(integers(min_value=0, max_value=42), min_size=1),
			min_size=1))
	def test_get_report(self, d):
		for error, lines in d.items():
			self.rep.add(lines, error)
		
		rep = self.rep.get_report()
		self.assertEqual(len(rep.splitlines()), len(d))
		
		self.rep.clear()
	
	
	@given(lists(tuples(integers(min_value=0, max_value=42),
			text(alphabet=string.ascii_letters, min_size=1)),
			min_size=1))
	def test_get_linewise_report(self, li):
		for line, error in li:
			self.rep.add([line], error)
		
		rep = self.rep.get_report(linewise=True)
		self.assertEqual(len(rep.splitlines()), len(li))
		
		self.rep.clear()


