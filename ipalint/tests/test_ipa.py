from unittest import TestCase

from hypothesis.strategies import text
from hypothesis import given

from ipalint.ipa import IPA_DATA_PATH, Symbol, UnknownSymbol
from ipalint.ipa import IPADataError, Tokeniser



class TokeniserTestCase(TestCase):
	
	def setUp(self):
		self.tok = Tokeniser()
	
	
	def test_load_ipa_data(self):
		ipa = self.tok._load_ipa_data(IPA_DATA_PATH)
		self.assertEqual(len(ipa), 170)
		
		self.assertEqual(ipa['p'], 'vl bilabial plosive')
		self.assertEqual(ipa['ʘ'], 'bilabial click')
		self.assertEqual(ipa['||'], 'major (intonational) group')
		self.assertEqual(ipa['↘'], 'global fall')
	
	
	@given(text().filter(lambda x: x != IPA_DATA_PATH))
	def test_load_ipa_error(self, path):
		with self.assertRaises(IPADataError):
			with self.assertLogs():
				self.tok._load_ipa_data(path)
	
	
	def test_tokenise(self):
		sym, unk = self.tok.tokenise('aɪ pʰiː eɪ')
		self.assertEqual(sym[0], Symbol('a', 'LATIN SMALL LETTER A', 'open front unrounded vowel'))
	
	
	@given(text())
	def test_tokenise_does_not_break(self, t):
		sym, unk = self.tok.tokenise(t)
		self.assertTrue(all([isinstance(i, Symbol) for i in sym]))
		self.assertTrue(all([isinstance(i, UnknownSymbol) for i in unk]))
