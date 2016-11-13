import logging.config
import logging

from ipalint.ipa import Recogniser
from ipalint.read import Reader
from ipalint.report import Reporter
from ipalint.strnorm import Normaliser



"""
The default logging configuration to be used; it will be slightly altered if
the verbose flag is set (see Core.__init__).
"""
DEFAULT_LOGGING = {
	'version': 1,
	'formatters': {
		'simple': {
			'format': '%(message)s'
		}
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
			'level': logging.DEBUG,
			'formatter': 'simple'
		}
	},
	'root': {
		'handlers': ['console'],
		'level': logging.INFO
	}
}



class Core:
	"""
	The controller singleton, an instance of which should be always present.
	This is what stays behind the cli and orchestrates the other modules.
	"""
	
	def __init__(self, verbose=False):
		"""
		Constructor. Configures the logging. The verbosity flag determines
		whether the min log level would be DEBUG or INFO.
		"""
		config = dict(DEFAULT_LOGGING)
		
		if verbose:
			config['root']['level'] = logging.DEBUG
		
		logging.config.dictConfig(config)
		
		self.log = logging.getLogger(__name__)
	
	
	def lint(self, dataset=None, col=None, no_header=False,
				ignore_nfd=False, ignore_ws=False, linewise=False, no_lines=False):
		"""
		Returns a string containing all the issues found in the dataset
		defined by the given file path.
		"""
		reader = Reader(dataset, has_header=not no_header, ipa_col=col)
		
		recog = Recogniser()
		norm = Normaliser(nfc_chars=recog.get_nfc_chars())
		
		for ipa_string, line_num in reader.gen_ipa_data():
			ipa_string = norm.normalise(ipa_string, line_num)
			recog.recognise(ipa_string, line_num)
		
		rep = Reporter()
		norm.report(rep, ignore_nfd, ignore_ws)
		recog.report(rep)
		
		return rep.get_report(linewise, no_lines)


