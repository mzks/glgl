#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, re, ast
from setuptools import setup, find_packages


PACKAGE_NAME = 'glgl'
with open(os.path.join(PACKAGE_NAME, '__init__.py')) as f:
    match = re.search(r'__version__\s+=\s+(.*)', f.read())
version = str(ast.literal_eval(match.group(1)))

setup(
    name="glgl",
    version=version,
    url='https://github.com/mzks/glgl',
    author='Keita Mizukoshi',
    author_email='mizukoshi.keita@jaxa.jp',
    maintainer='Keita Mizukoshi',
    maintainer_email='mizukoshi.keita@jaxa.jp',
    description='GL840 control tool',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['PyMySQL', 'numpy', 'psutil'],
    license="MIT",
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
    'console_scripts': [ 'glgl=glgl.cli:main' ]
    }
)
