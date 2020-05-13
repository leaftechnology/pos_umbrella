# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in pos_umbrella/__init__.py
from pos_umbrella import __version__ as version

setup(
	name='pos_umbrella',
	version=version,
	description='POS Umbrella',
	author='jan',
	author_email='janlloydangeles@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
