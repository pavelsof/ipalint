import argparse
import sys

from ipalint.core import Core
from ipalint import __version__



class Cli:
	"""
	Singleton that handles the user input, inits the whole machinery, and takes
	care of exiting the programme.
	"""
	
	def __init__(self):
		"""
		Constructor. Inits the argparse parser.
		"""
		usage = 'ipalint dataset [options]'
		desc = ('simple linter that checks datasets for '
				'IPA errors and inconsistencies')
		
		self.parser = argparse.ArgumentParser(usage=usage,
				description=desc, add_help=False)
		
		input_args = self.parser.add_argument_group('dataset arguments')
		input_args.add_argument('dataset', nargs='?', default=sys.stdin, help=(
			'the dataset file to be linted; '
			'if omitted, ipalint reads from stdin '
			'(thus, ipalint X and cat X | ipalint are equivalent)'))
		input_args.add_argument('--col', help=(
			'specify the column containing the IPA data; '
			'this could be the column index (starting from 0) '
			'or the column name (if there is a header row)'))
		input_args.add_argument('--no-header', action='store_true', help=(
			'do not skip the first row of the file; '
			'if this flag is not set, the first row will be skipped'))
		
		output_args = self.parser.add_argument_group('output arguments')
		output_args.add_argument('--ignore-nfd', action='store_true', help=(
			'ignore warnings about strings that are not compliant with '
			'Unicode\'s NFD normal form'))
		output_args.add_argument('--ignore-ws', action='store_true', help=(
			'ignore warnings about whitespace issues '
			'(e.g. leading or trailing whitespace)'))
		output_args.add_argument('--linewise', action='store_true', help=(
			'show errors line-by-line; '
			'by default each error is only shown once with '
			'the offending lines\' numbers stacked together'))
		output_args.add_argument('--no-lines', action='store_true', help=(
			'only show the error messages, '
			'without the line numbers where the errors originate; '
			'ignored if --linewise is set'))
		
		meta_args = self.parser.add_argument_group('meta arguments')
		meta_args.add_argument('-h', '--help', action='help', help=(
			'show this help message and exit'))
		meta_args.add_argument('-v', '--version', action='version',
			version=__version__,
			help='show the version number and exit')
	
	
	def run(self, raw_args=None):
		"""
		Parses the given arguments (if these are None, then argparse's parser
		defaults to parsing sys.argv), inits a Core instance, calls its lint
		method with the respective arguments, and then exits.
		"""
		args = self.parser.parse_args(raw_args)
		
		core = Core()
		
		try:
			report = core.lint(**vars(args))
		except Exception as err:
			self.parser.error(str(err))
		
		print(report)
		self.parser.exit()



def main():
	"""
	The (only) entry point for the command-line interface as registered in
	setup.py. Inits a Cli instance and runs it with sys.argv.
	"""
	cli = Cli()
	cli.run()


