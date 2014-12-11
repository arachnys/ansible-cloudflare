#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='ansible-cloudflare',
    version='0.1',
    author='Marcus Fredriksson',
    author_email='drmegahertz@gmail.com',
    install_requires=['ansible'],
    package_dir={'': 'src'},
    packages=['ansible.modules.extras.cloud'],
)