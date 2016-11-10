import sys

from unittest.mock import patch
from unittest import TestCase

from hypothesis.strategies import fixed_dictionaries, sampled_from, text
from hypothesis import given

from ipalint.cli import Cli
from ipalint.core import Core



class CliTestCase(TestCase):
	
	def setUp(self):
		self.cli = Cli()
	
	@given(text().filter(lambda t: not t.startswith('-')),
			text().filter(lambda t: not t.startswith('-')),
			fixed_dictionaries({
				'no_header': sampled_from(['--no-header', '']),
				'ignore_nfd': sampled_from(['--ignore-nfd', '']),
				'ignore_ws': sampled_from(['--ignore-ws', '']),
				'linewise': sampled_from(['--linewise', '']),
				'no_lines': sampled_from(['--no-lines', ''])}))
	def test_run(self, dataset, col, flags):
		args = [dataset]
		if col: args.extend(['--col', col])
		args.extend([flag for flag in flags.values() if flag])
		
		with patch.object(Core, 'lint', return_value='42') as mock_lint:
			with patch.object(sys.stdout, 'write'):
				try:
					self.cli.run(args)
				except SystemExit:
					pass
				
				mock_lint.assert_called_once_with(
					dataset = dataset,
					col = col if col else None,
					no_header = True if flags['no_header'] else False,
					ignore_nfd = True if flags['ignore_nfd'] else False,
					ignore_ws = True if flags['ignore_ws'] else False,
					linewise = True if flags['linewise'] else False,
					no_lines = True if flags['no_lines'] else False)


