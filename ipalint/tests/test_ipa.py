import os.path
import string

from unittest import TestCase

from hypothesis.strategies import integers, text
from hypothesis import assume, given

from ipalint.ipa import IPA_DATA_PATH, COMMON_ERR_DATA_PATH
from ipalint.ipa import Symbol, UnknownSymbol
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
	
	
	@given(text(alphabet=string.printable))
	def test_load_ipa_error(self, path):
		assume(not os.path.exists(path))
		
		with self.assertRaises(IPADataError):
			with self.assertLogs():
				self.recog._load_ipa_data(path)
	
	
	def test_load_common_err_data(self):
		data = self.recog._load_common_err_data(COMMON_ERR_DATA_PATH)
		self.assertEqual(data['?'], 'ʔ')
		self.assertEqual(data['ʦ'], 't͡s')
		self.assertEqual(data['ʥ'], 'd͡ʑ')
		self.assertEqual(data[':'], 'ː')
	
	
	@given(text(alphabet=string.printable))
	def test_load_common_err_data_error(self, path):
		assume(not os.path.exists(path))
		
		with self.assertRaises(IPADataError):
			with self.assertLogs():
				self.recog._load_common_err_data(path)
	
	
	def test_get_nfc_chars(self):
		s = self.recog.get_nfc_chars()
		self.assertEqual(s, set(['ç']))
	
	
	def test_recognise(self):
		sym, unk = self.recog.recognise('aɪ pʰiː eɪ', 0)
		self.assertEqual(len(sym), 8)
		self.assertEqual(len(unk), 0)
		
		self.assertEqual(sym[0], Symbol('a', 'LATIN SMALL LETTER A', 'open front unrounded vowel'))
		self.assertEqual(sym[1], Symbol('ɪ', 'LATIN LETTER SMALL CAPITAL I', 'lowered-close front unrounded vowel'))
		
		self.assertEqual(sym[2], Symbol('p', 'LATIN SMALL LETTER P', 'vl bilabial plosive'))
		self.assertEqual(sym[3], Symbol('ʰ', 'MODIFIER LETTER SMALL H', 'aspirated'))
		self.assertEqual(sym[4], Symbol('i', 'LATIN SMALL LETTER I', 'close front unrounded vowel'))
		self.assertEqual(sym[5], Symbol('ː', 'MODIFIER LETTER TRIANGULAR COLON', 'long'))
		
		self.assertEqual(sym[6], Symbol('e', 'LATIN SMALL LETTER E', 'close-mid front unrounded vowel'))
		self.assertEqual(sym[7], Symbol('ɪ', 'LATIN LETTER SMALL CAPITAL I', 'lowered-close front unrounded vowel'))
	
	
	@given(text(), integers(min_value=0))
	def test_recognise_does_not_break(self, t, i):
		sym, unk = self.recog.recognise(t, i)
		self.assertTrue(all([isinstance(i, Symbol) for i in sym]))
		self.assertTrue(all([isinstance(i, UnknownSymbol) for i in unk]))


