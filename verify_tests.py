#!/usr/bin/env python
import sys
sys.path.insert(0, 'agent')
from diagramscene_functional_tests import DiagramSceneFunctionalTests

dt = DiagramSceneFunctionalTests()
tests = dt.build_all_tests()

print(f'Total tests: {len(tests)}\n')
print('Test Commands Summary:')
print('-' * 70)
for i, t in enumerate(tests, 1):
    print(f'{i:2d}. {t["test"]:30s} | {len(t["commands"])} cmds | Status: {t["status"]}')
    for cmd in t["commands"]:
        print(f'    -> {cmd}')

# Count executable commands (those with echo, not comments)
executable_count = sum(1 for t in tests if any('echo' in cmd for cmd in t['commands']))
print(f'\nExecutable tests (with echo): {executable_count}/{len(tests)}')
