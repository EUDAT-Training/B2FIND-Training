#bootstrap easy_install
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

description = \
"""
This package is used to create individual Dublin Core records from a given tabular (tsv) or comma (csv) separated file.
"""

install_requires = []
try:
  import DublinCoreTerms
except ImportError:
  install_requires.append('dublincore>=1.0')

setup (
    name = 'md-convert',
    version = '0.1.0',
    url = 'https://github.com/hwidmann/MD-Convert',
    author = 'Heinrich Widmann',
    author_email = 'widmann@dkrz.de',
    py_modules = ['DublinCoreTerms'],
    scripts = ['md-convert.py'],
    description = description,
    platforms = ['POSIX'],
    test_suite = 'test'
)  
