import os.path

from setuptools import setup, find_packages



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(BASE_DIR, 'README.rst')) as f:
	README = f.read()



setup(
	name = 'ipalint',
	version = '0.0.0',
	
	description = (
		'simple linter that checks datasets '
		'for IPA errors and inconsistencies'),
	long_description = README,
	
	# url = '',
	
	author = 'Pavel Sofroniev',
	author_email = 'pavelsof@gmail.com',
	
	license = 'MIT',
	
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Text Processing :: Linguistic'
	],
	keywords = 'IPA lint',
	
	packages = find_packages(),
	package_data = {'ipalint': ['data/*', 'tests/fixtures/*']},
	
	install_requires = [],
	
	test_suite = 'ipalint.tests',
	tests_require = ['hypothesis >= 3.5'],
	
	entry_points = {
		'console_scripts': [
			'ipalint = ipalint.cli:main'
		]
	}
)
