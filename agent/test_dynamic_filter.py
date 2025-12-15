#!/usr/bin/env python3
"""
Small helper to exercise the dynamic output filtering used by FlaskApp.
Run this to verify long test-list lines are removed from the UI summary.
"""
import textwrap

raw = textwrap.dedent('''
C++ runtime: Builds and runs the C++ binary (checks for crashes and expected behavior).
injected_cmake_build:D:\\semester5\\quality\\ai-agent-project\\agent\\workspaces\\utnubu__source_20251212_162419\\cpp_project\\diagramscene_ultima\\release\\injected_whitebox_tests: Automatic or workspace-provided test. See details for commands and output.
Resource Management: Verifies that temporary resources (files, handles) are managed correctly.
Concurrency: Executes simple threaded tasks to detect obvious deadlocks or exceptions.
Boundary Test: Feeds extreme or malformed inputs to check boundary handling.
Boundary Test aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: Feeds extreme or malformed inputs to check boundary handling.
Boundary Test -1: Feeds extreme or malformed inputs to check boundary handling.
Boundary Test 0: Feeds extreme or malformed inputs to check boundary handling.
Boundary Test 10000000000.0: Feeds extreme or malformed inputs to check boundary handling.
Boundary Test ('int', 'a'): Feeds extreme or malformed inputs to check boundary handling.
Boundary Test ('float', 'b'): Feeds extreme or malformed inputs to check boundary handling.
Env Test: Validates that required environment variables are set for runtime.
Dynamic Code Test: Runs a small dynamic code execution check to ensure sandboxing and error handling.
run_executable: Automatic or workspace-provided test. See details for commands and output.
readme_exists: Automatic or workspace-provided test. See details for commands and output.
TC-1.1: Rectangle Drawing: Automatic or workspace-provided test. See details for commands and output.
TC-1.2: Circle Drawing: Automatic or workspace-provided test. See details for commands and output.
TC-1.3: Diamond Drawing: Automatic or workspace-provided test. See details for commands and output.
TC-1.4: Arrow Drawing: Automatic or workspace-provided test. See details for commands and output.
TC-2.1: Element Connection: Automatic or workspace-provided test. See details for commands and output.
TC-2.2: Auto Alignment: Automatic or workspace-provided test. See details for commands and output.
TC-2.3: Smart Routing: Automatic or workspace-provided test. See details for commands and output.
TC-3.1: Element Selection: Automatic or workspace-provided test. See details for commands and output.
TC-3.2: Element Movement: Automatic or workspace-provided test. See details for commands and output.
TC-3.3: Element Deletion: Automatic or workspace-provided test. See details for commands and output.
TC-3.4: Copy/Paste: Automatic or workspace-provided test. See details for commands and output.
TC-3.5: Undo/Redo: Automatic or workspace-provided test. See details for commands and output.
TC-4.1: Color Settings: Automatic or workspace-provided test. See details for commands and output.
TC-4.2: Size Adjustment: Automatic or workspace-provided test. See details for commands and output.
TC-4.3: Label Editing: Automatic or workspace-provided test. See details for commands and output.
TC-4.4: Shape Type Conversion: Automatic or workspace-provided test. See details for commands and output.
TC-5.1: Load Template: Automatic or workspace-provided test. See details for commands and output.
TC-5.2: Save as Template: Automatic or workspace-provided test. See details for commands and output.
TC-6.1: Export PNG: Automatic or workspace-provided test. See details for commands and output.
TC-6.2: Export PDF: Automatic or workspace-provided test. See details for commands and output.
TC-6.3: Export SVG: Automatic or workspace-provided test. See details for commands and output.
TC-7.1: Import Visio: Automatic or workspace-provided test. See details for commands and output.
GUI smoke (AHK): Automatic or workspace-provided test. See details for commands and output.
dont show this texts at the ui above the table
''')

hide_prefixes = (
    'TC-',
    'Boundary Test',
    'GUI smoke',
    'run_executable',
    'readme_exists',
    'Env Test',
    'Dynamic Code Test',
    'C++ runtime',
    'injected_cmake_build',
    'Resource Management',
    'Concurrency',
)

def filter_dynamic_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    # remove lines starting with 'Patches applied:' as original code did
    lines = [ln for ln in lines if not ln.strip().startswith('Patches applied:')]
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append(ln)
            continue
        if any(s.startswith(pref) for pref in hide_prefixes):
            continue
        out.append(ln)
    return '\n'.join(out)


if __name__ == '__main__':
    print('--- Raw ---')
    print(raw)
    print('\n--- Filtered ---')
    print(filter_dynamic_text(raw))
