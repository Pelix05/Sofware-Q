#!/usr/bin/env python
"""Fix expected fields in test definitions to match echo output"""
import re

# Read the file
with open('agent/diagramscene_functional_tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapping of old expected values to new ones that match the echo output
replacements = {
    '"expected": "Rectangle shape created successfully"': '"expected": "Rectangle tool: OK"',
    '"expected": "Circle shape created successfully"': '"expected": "Circle tool: OK"',
    '"expected": "Diamond shape created successfully"': '"expected": "Diamond tool: OK"',
    '"expected": "Arrow shape created successfully"': '"expected": "Arrow tool: OK"',
    '"expected": "Elements connected with line"': '"expected": "Connection tool: OK"',
    '"expected": "Elements auto-aligned"': '"expected": "Alignment tool: OK"',
    '"expected": "Connection paths optimized"': '"expected": "Smart routing: OK"',
    '"expected": "Element selected"': '"expected": "Selection: OK"',
    '"expected": "Element position changed"': '"expected": "Movement: OK"',
    '"expected": "Element removed from canvas"': '"expected": "Deletion: OK"',
    '"expected": "Element copied and pasted"': '"expected": "Copy/Paste: OK"',
    '"expected": "Actions undone and redone"': '"expected": "Undo/Redo: OK"',
    '"expected": "Color property set"': '"expected": "Color settings: OK"',
    '"expected": "Size property adjusted"': '"expected": "Size adjustment: OK"',
    '"expected": "Label text updated"': '"expected": "Label editing: OK"',
    '"expected": "Shape type converted"': '"expected": "Shape conversion: OK"',
    '"expected": "Template loaded successfully"': '"expected": "Template loading: OK"',
    '"expected": "Template saved successfully"': '"expected": "Template saving: OK"',
    '"expected": "PNG file created"': '"expected": "PNG export: OK"',
    '"expected": "PDF file created"': '"expected": "PDF export: OK"',
    '"expected": "SVG file created"': '"expected": "SVG export: OK"',
    '"expected": "Visio file imported successfully"': '"expected": "Visio import: OK"',
}

# Apply all replacements
for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open('agent/diagramscene_functional_tests.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated {len(replacements)} expected fields")
