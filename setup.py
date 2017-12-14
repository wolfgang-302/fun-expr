#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 12:40:18 2017

@author: wolfgang-302
"""

from distutils.core import setup

setup(name='fun-expr',
      version='0.1',
      description='Create a sympy function from an expression',
      author='wolfgang-302',
      author_email='11839527+wolfgang-302@users.noreply.github.com',
      packages=['fun-expr'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          ],
      install_requires=['sympy'],
      license='MIT License',
      )

