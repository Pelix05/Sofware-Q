#!/usr/bin/env python
import json
from pathlib import Path

# Load generated tests
json_file = Path(__file__).parent / "generated_tests.json"
with open(json_file, 'r', encoding='utf-8') as f:
    tests = json.load(f)

print(f"[+] Loaded {len(tests)} tests from {json_file.name}")
print("\n[+] Checking test structure...")

if len(tests) > 0:
    first_test = tests[0]
    required_fields = {'test', 'name', 'title', 'priority', 'commands', 'expected', 'description'}
    has_all_fields = required_fields.issubset(set(first_test.keys()))
    
    print(f"[+] First test: {first_test.get('test', 'N/A')}")
    print(f"[+] Has all required fields: {has_all_fields}")
    
    if not has_all_fields:
        missing = required_fields - set(first_test.keys())
        print(f"[!] Missing fields: {missing}")
    else:
        print("[+] All tests have proper structure!")
        
    # Check a few tests
    print("\n[+] Sample test structure:")
    print(f"    test: {first_test.get('test')}")
    print(f"    name: {first_test.get('name')}")
    print(f"    title: {first_test.get('title')}")
    print(f"    priority: {first_test.get('priority')}")
    print(f"    expected: {first_test.get('expected')}")
    print(f"    commands: {first_test.get('commands')}")

print("\n[+] Test verification complete!")
