from unittest import TestCase

from hypothesis.strategies import integers, text
from hypothesis import given

from ipalint.ipa import IPA_DATA_PATH, Symbol, UnknownSymbol
from ipalint.ipa import IPADataError, Recogniser



class RecogniserTestCase(TestCase):
	
	def setUp(self):
		self.recog = Recogniser()
	
	
	def test_load_ipa_data(self):
		ipa = self.recog._load_ipa_data(IPA_DATA_PATH)
		self.assertEqual(len(ipa), 170)
		
		self.assertEqual(ipa['p'], 'vl bilabial plosive')
		self.assertEqual(ipa['ʘ'], 'bilabial click')
		self.assertEqual(ipa['||'], 'major (intonational) group')
		self.assertEqual(ipa['↘'], 'global fall')
	
	
	@given(text().filter(lambda x: x != IPA_DATA_PATH))
	def test_load_ipa_error(self, path):
		with self.assertRaises(IPADataError):
			with self.assertLogs():
				self.recog._load_ipa_data(path)
	
	
	def test_recognise(self):
		sym, unk = self.recog.recognise('aɪ pʰiː eɪ', 0)
		self.assertEqual(sym[0], Symbol('a', 'LATIN SMALL LETTER A', 'open front unrounded vowel'))
	
	
	@given(text(), integers(min_value=0))
	def test_recognise_does_not_break(self, t, i):
		sym, unk = self.recog.recognise(t, i)
		self.assertTrue(all([isinstance(i, Symbol) for i in sym]))
		self.assertTrue(all([isinstance(i, UnknownSymbol) for i in unk]))


