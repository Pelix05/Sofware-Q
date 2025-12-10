#!/usr/bin/env python
"""Test the real tests generation"""
import sys
sys.path.insert(0, 'agent')

from diagramscene_real_tests import generate_diagramscene_real_tests

tests = generate_diagramscene_real_tests()
print(f'Generated {len(tests)} real tests')
print(f'First test: {tests[0]["test"]}')
print(f'Command: {tests[0]["commands"][0]}')
