import unicodedata

from unittest import TestCase

from hypothesis.strategies import text
from hypothesis import given

from ipalint.strnorm import Normaliser



class NormaliserTestCase(TestCase):
	def setUp(self):
		self.norm = Normaliser()
	
	@given(text())
	def test_normalise(self, t):
		res = self.norm.normalise(t, 0)
		
		self.assertEqual(res.strip(), res)
		self.assertEqual(unicodedata.normalize('NFD', res), res)


