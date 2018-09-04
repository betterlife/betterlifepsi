# coding=utf-8

import re
import ast
from setuptools import setup
from os import path

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('psi/app/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('requirements/common.txt', 'r') as f:
    install_reqs = [
        s for s in [
            line.strip(' \n') for line in f
        ] if not s.startswith('#') and s != ''
    ]

with open('requirements/test.txt', 'r') as f:
    tests_reqs = [
        s for s in [
            line.strip(' \n') for line in f
        ] if not s.startswith('#') and s != '' and not s.startswith('-r ')
    ]

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="betterlifepsi",
    version=version,
    packages=['psi'],
    include_package_data=True,
    author="Lawrence Liu",
    author_email="lawrence@betterlife.io",
    description="Betterlife Intelligent PSI(Purchase, Sales and Inventory) system",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    keywords="Betterlife, Intelligent, Purchase Order, Sales Order, Inventory Management, Retail",
    url="https://github.com/betterlife/psi",
    install_requires=install_reqs,
    tests_require=tests_reqs,
    setup_requires=install_reqs,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English',
        'Framework :: Flask',
    ],
)
