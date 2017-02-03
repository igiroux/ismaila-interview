'''
Simple e-commerce app
'''

import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'VERSION.txt')) as fp:
    VERSION = fp.read().strip()
setup(
    name='zenmarket',
    version=VERSION,
    packages=find_packages(),
    install_requires=['click', 'colander', 'aiohttp'],
    extras_require={
        'dev': ['ipdb', 'ipython', 'pytest', 'pytest-cov', 'pytest-pylint'],
    },
    entry_points='''
        [console_scripts]
        level1=zenmarket.level1:main
        level2=zenmarket.level2:main
    ''',
)
