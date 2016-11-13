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
		self.assertEqual(res, unicodedata.normalize('NFD', t.strip()))
	
	
	def test_normalise_cedilla(self):
		norm = Normaliser(['ç'])
		
		res = norm.normalise(' çáç ', 0)
		self.assertEqual(res, 'çáç')


