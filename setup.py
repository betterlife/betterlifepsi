# coding=utf-8

import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('app/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name="Betterlife PSI",
    version=version,
    packages=['app', 'migrations'],
    include_package_data=True,
    author="Lawrence Liu",
    author_email="lawrence@betterlife.io",
    description="Betterlife Intelligent PSI(Purchase, Sales and Inventory) system",
    license="MIT",
    keywords="Betterlife, Intelligent, Purchase, Sales, Inventory",
    url="https://github.com/betterlife/psi",
    install_requires=[
        "Flask>=0.11.1",
        "Flask-SQLAlchemy==2.0",
        "Flask-SSLify==0.1.5",
        "Jinja2==2.7.3",
        "MarkupSafe==0.23",
        "SQLAlchemy==1.0.4",
        "Werkzeug==0.10.4",
        "gunicorn==19.3.0",
        "itsdangerous==0.24",
        "psycopg2==2.6",
        "wsgiref==0.1.2",
        "Babel==1.3",
        "Flask_BabelEx==0.9.2",
        "Flask-Migrate==1.4.0",
        "blinker==1.4.0",
        "raven==5.10.2",
        "Flask-Security==1.7.5",
        "Flask-DebugToolbar==0.10.0",
    ],
    tests_require=[
        "coverage==3.7.1",
        "nose==1.3.7",
        "codecov==2.0.3",
        "fake-factory==0.5.8",
    ],
    setup_requires=['nose==1.3.7'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Natural Language :: Chinese (Simplified)',
        'Framework :: Flask',
     ],
)
