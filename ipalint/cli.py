import argparse

from ipalint.core import Core



class Cli:
	"""
	Singleton that handles the user input, inits the whole machinery, and takes
	care of exiting the programme.
	"""
	
	def __init__(self):
		"""
		Constructor. Inits the argparse parser.
		"""
		self.parser = argparse.ArgumentParser()
		
		self.parser.add_argument('datafile', help=(
			'the data file to be linted; '
			'possible formats are csv/tsv'))
		
		self.parser.add_argument('-f', '--fix', action='store_true', help=(
			'create a copy of the original file '
			'but with the IPA data fixed'))
		self.parser.add_argument('-c', '--col', help=(
			'specify the column with the IPA data; '
			'generally ipalint should be clever enough '
			'to infer which the column is'))
		self.parser.add_argument('-nh', '--no-header', action='store_true', help=(
			'do not skip the first row of the file; '
			'the default is true (it will be skipped)'))
		self.parser.add_argument('-v', '--verbose', action='store_true',
			help='print debug info')
	
	
	def run(self, raw_args=None):
		"""
		Parses the given arguments (or, except for in unit testing, sys.argv),
		inits the Core instance and transfers to that. Note that if raw_args is
		None, then argparse's parser defaults to reading sys.argv.
		
		Returns a human-readable string to be printed to the user.
		"""
		args = self.parser.parse_args(raw_args)
		
		core = Core(args.verbose)



def main():
	"""
	The (only) entry point for the command-line interface as registered in
	setup.py. Inits a Cli instance, runs it with sys.argv, and prints the
	output to stdout.
	"""
	cli = Cli()
	res = cli.run()
	if res: print(res.strip())
