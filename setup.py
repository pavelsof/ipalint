import os.path

from setuptools import setup, find_packages



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(BASE_DIR, 'README.rst')) as f:
	README = f.read()



setup(
	name = 'ipalint',
	version = '0.0.0',
	
	description = 'IPA linter',
	long_description = README,
	
	author = 'Pavel Sofroniev',
	author_email = 'pavelsof@gmail.com',
	
	license = 'MIT',
	
	classifiers = [
		'Development Status :: 1 - Planning',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Text Processing :: Linguistic'
	],
	keywords = 'IPA lint',
	
	packages = find_packages(),
	install_requires = [],
	
	test_suite = 'ipalint.tests',
	tests_require = ['hypothesis >= 3.5'],
	
	entry_points = {
		'console_scripts': [
			'ipalint = ipalint.cli:main'
		]
	}
)
