# -*- coding: utf-8 -*-
import codecs
import re
from os import path
from distutils.core import setup
from setuptools import find_packages


def read(*parts):
    return codecs.open(path.join(path.dirname(__file__), *parts),
                       encoding='utf-8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='annotatedocs',
    version=find_version('annotatedocs', '__init__.py'),
    author=u'Gregor Müllegger',
    author_email='gregor@muellegger.de',
    packages=find_packages(),
    include_package_data=True,
    scripts=[
        'scripts/annotatedocs',
        'scripts/doctree2rdf',
        'scripts/rdfquery',
        'scripts/rdfconcat',
    ],
    install_requires=[
        'click>=2.0'
        'logbook',
        'nltk',
        'rdflib',
        'sh',
        'slumber',
        'Sphinx',
        'virtualenv',
        'sphinx_rtd_theme_annotated',
    ],
    url='',
    license=u'Copyright by Gregor Müllegger',
    description='',
    long_description=read('README.rst'),
    classifiers=[],
    zip_safe=False,
)
