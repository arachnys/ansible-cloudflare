#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='ansible-cloudflare',
    version='0.1',
    description='An ansible module for managing CloudFlare DNS records.',
    long_description=long_description,
    author='Marcus Fredriksson',
    author_email='drmegahertz@gmail.com',
    url='https://github.com/DrMegahertz/ansible-cloudflare/',
    install_requires=['ansible'],
    package_dir={'': 'src'},
    packages=['ansible.modules.extras.cloud'],
)