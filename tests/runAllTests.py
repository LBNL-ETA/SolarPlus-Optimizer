# -*- coding: utf-8 -*-
"""
This script run all tests in the test folder.

"""
import unittest
import os

loader = unittest.TestLoader()
start_dir = os.path.abspath(os.path.join(__file__,'..'))
suite = loader.discover(start_dir)
print('Loading tests...')
runner = unittest.TextTestRunner()
runner.run(suite)
