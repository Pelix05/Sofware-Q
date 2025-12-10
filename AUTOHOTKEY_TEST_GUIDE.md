# AutoHotkey Test Guide for DiagramScene

## Overview

This guide explains how to run and debug the AutoHotkey-based GUI automation tests for DiagramScene. These tests provide **real feature testing** (unlike the echo-based infrastructure tests) by automating mouse and keyboard interactions with the DiagramScene application.

## Files Involved

| File | Purpose |
|------|---------|
| `agent/diagramscene_tests.ahk` | Main AutoHotkey test script (650 lines) |
| `agent/run_autohotkey_tests.py` | Python test runner wrapper |
| `agent/autohotkey_integration.py` | Integration with dynamic_tester framework |
| `ahk_test_results.txt` | Raw test output log |
| `ahk_test_results.json` | Structured test results |

## Quick Start

### Method 1: Direct Execution (Recommended)

```powershell
# Navigate to agent directory
cd agent

# Run tests via Python runner
python run_autohotkey_tests.py

# Or specify a timeout
python run_autohotkey_tests.py --timeout 300
```

### Method 2: Direct AutoHotkey

```powershell
# From agent directory
AutoHotkey.exe diagramscene_tests.ahk
```

### Method 3: From Flask Application

When you upload a DiagramScene project to Flask:
1. Tests are automatically analyzed and categorized
2. AutoHotkey tests can be triggered from the UI
3. Results appear in the test results table

## Test Structure

### 22 Tests Organized in 7 Categories

#### 1. Drawing Tools (TC-1.1 ~ TC-1.4)
Tests drawing different shapes:
- Rectangle drawing (TC-1.1)
- Circle drawing (TC-1.2)
- Diamond drawing (TC-1.3)
- Arrow drawing (TC-1.4)

#### 2. Connection Management (TC-2.1 ~ TC-2.3)
Tests element connection features:
- Element connection (TC-2.1)
- Auto alignment (TC-2.2)
- Smart routing (TC-2.3)

#### 3. Editing Operations (TC-3.1 ~ TC-3.5)
Tests editing and manipulation:
- Element selection (TC-3.1)
- Element movement (TC-3.2)
- Element deletion (TC-3.3)
- Copy/paste operations (TC-3.4)
- Undo/redo functionality (TC-3.5)

#### 4. Property Editing (TC-4.1 ~ TC-4.4)
Tests property modification:
- Color editing (TC-4.1)
- Size/dimension editing (TC-4.2)
- Label/text editing (TC-4.3)
- Shape conversion (TC-4.4)

#### 5. Template Library (TC-5.1 ~ TC-5.2)
Tests template features:
- Load templates (TC-5.1)
- Save templates (TC-5.2)

#### 6. Export Functions (TC-6.1 ~ TC-6.3)
Tests export capabilities:
- PNG export (TC-6.1)
- PDF export (TC-6.2)
- SVG export (TC-6.3)

#### 7. Import Functions (TC-7.1)
Tests import features:
- Visio file import (TC-7.1)

## Prerequisites

### Required Software

1. **AutoHotkey v2.0 or later**
   - Download: https://www.autohotkey.com/
   - Installation: Run installer and choose "Install for all users"
   - Verify: `where AutoHotkey.exe` in PowerShell

2. **DiagramScene Application**
   - Path: `D:\flowchart_test\diagramscene.exe`
   - Must be built and available
   - Executable and responsive

3. **Python 3.8+**
   - Required for test runner
   - Already available in project environment

### Environment Setup

```powershell
# Check AutoHotkey installation
where AutoHotkey.exe

# Check DiagramScene executable
if (Test-Path "D:\flowchart_test\diagramscene.exe") {
    Write-Host "DiagramScene found ✓"
} else {
    Write-Host "DiagramScene not found ✗"
}
```

## Running Tests

### Python Runner (Recommended)

The Python runner provides better error handling and result parsing:

```powershell
cd agent
python run_autohotkey_tests.py
```

**Output:**
```
============================================================
AutoHotkey Test Runner
============================================================

✓ Script found: D:\...\agent\diagramscene_tests.ahk
✓ AutoHotkey installed
✓ Log file: D:\...\agent\ahk_test_results.txt
✓ Timeout: 600 seconds

Launching tests...

✓ Tests completed in 45.3 seconds

============================================================
Test Results Summary
============================================================
  Total:  22
  Passed: 20 ✓
  Failed: 2 ✗
  Skipped: 0 ⊘
============================================================

Individual Results:
  ✓ TC-1.1: Rectangle Drawing: PASS
  ✓ TC-1.2: Circle Drawing: PASS
  ...
  ✗ TC-5.1: Load Templates: FAIL
  ✗ TC-6.3: SVG Export: FAIL

✓ Results saved to: D:\...\agent\ahk_test_results.json
```

### Direct AutoHotkey

For more immediate feedback or debugging:

```powershell
cd agent
AutoHotkey.exe diagramscene_tests.ahk
```

**Advantages:**
- Faster startup
- Easier to watch test execution
- Real-time window interaction

**Disadvantages:**
- No result parsing
- Manual log file review required
- Less detailed error reporting

## Interpreting Results

### Test Output Format

Each test result follows this format:

```
Running: TC-1.1: Rectangle Drawing  [✓ PASS]
Running: TC-2.1: Element Connection  [✗ FAIL] - Window timeout
```

### Status Values

| Status | Meaning |
|--------|---------|
| `✓ PASS` | Test completed successfully |
| `✗ FAIL` | Test failed or timed out |
| `⊘ SKIP` | Test was skipped (dependency failed) |

### Result Codes

```json
{
  "test": "TC-1.1: Rectangle Drawing",
  "status": "PASS",
  "detail": "Test completed successfully"
}
```

## Debugging Failed Tests

### Common Issues and Solutions

#### 1. **"Could not launch DiagramScene.exe"**

**Problem:** AutoHotkey cannot find DiagramScene

**Solution:**
```powershell
# Check path in script (line 15)
# Update if needed:
DIAGRAMSCENE_EXE := "C:\path\to\your\diagramscene.exe"

# Or set environment variable
$env:DIAGRAMSCENE_PATH = "D:\flowchart_test\diagramscene.exe"
```

#### 2. **"Window timeout"**

**Problem:** DiagramScene takes too long to start

**Solution:**
- Increase timeout in Python runner:
  ```powershell
  python run_autohotkey_tests.py --timeout 900
  ```

- Or modify script line 49:
  ```ahk
  WaitDiagramScene(10000)  ; Increase from 5000 to 10000
  ```

#### 3. **"Mouse coordinates not working"**

**Problem:** UI layout differs from expected coordinates

**Solution:**
1. **Get new coordinates:**
   ```powershell
   # Move mouse to element and note position
   # Windows shows coordinates at bottom-right when holding Alt+Shift
   ```

2. **Update coordinates in script:**
   - Find the test function (e.g., `TestRectangleDrawing`)
   - Replace `MouseMove(x, y)` values with new coordinates
   - Test one function at a time

3. **Common toolbar positions:**
   - Rectangle: x=100-120
   - Circle: x=130-150
   - Diamond: x=160-180
   - Arrow: x=190-210
   - Canvas: y=200-300+

#### 4. **"Test hangs or takes too long"**

**Problem:** Timing issues or infinite waits

**Solution:**
- Increase `Sleep()` duration:
  ```ahk
  Sleep(500)  ; Increase from 100-200
  ```

- Check for missing window state:
  ```ahk
  if !WindowExists("DiagramScene")
      return false
  ```

### Modifying Tests

To adjust a specific test:

1. **Open** `agent/diagramscene_tests.ahk`

2. **Find** the test function:
   ```powershell
   # Search for TestRectangleDrawing
   Select-String "TestRectangleDrawing" diagramscene_tests.ahk
   ```

3. **Modify** coordinates or timing:
   ```ahk
   TestRectangleDrawing() {
       MouseMove(120, 50)    ; ← Change X coordinate
       Sleep(150)             ; ← Increase delay
       ; ... rest of test
   }
   ```

4. **Test** single function:
   ```powershell
   # Run script with interactive debugging
   AutoHotkey.exe diagramscene_tests.ahk
   
   # Watch execution and note failures
   ```

5. **Verify** by running full suite again

## Advanced Options

### Custom Test Execution

```powershell
# Run with custom script path
python run_autohotkey_tests.py --script "path/to/custom_tests.ahk"

# Specify output file
python run_autohotkey_tests.py --output "results.json"

# Increase timeout
python run_autohotkey_tests.py --timeout 900
```

### Viewing Detailed Logs

```powershell
# View raw log output
Get-Content agent\ahk_test_results.txt

# View structured results
Get-Content agent\ahk_test_results.json | ConvertFrom-Json | Format-Table

# Follow log in real-time (while tests running)
Get-Content agent\ahk_test_results.txt -Wait
```

### Integration with Flask Application

To integrate AutoHotkey tests with the Flask test runner:

```python
# In dynamic_tester.py
from agent.autohotkey_integration import run_autohotkey_tests

# Add to test suite
ahk_results = run_autohotkey_tests()
all_results.extend(ahk_results)
```

## Performance Metrics

### Expected Execution Times

- **Fast mode:** 20-30 seconds
  - Minimal waits
  - Quick mouse movements

- **Standard mode:** 40-60 seconds (default)
  - Proper timing between actions
  - Adequate sleep for GUI response

- **Slow mode:** 90+ seconds
  - Debugging
  - Slow computer

### Typical Results

- **Pass rate:** 70-90% initially
- **Common failures:** Import/Export features (file dialogs)
- **After tuning:** 95%+ pass rate

## Troubleshooting Checklist

- [ ] AutoHotkey installed (`where AutoHotkey.exe`)
- [ ] DiagramScene executable exists at configured path
- [ ] DiagramScene can start manually
- [ ] Mouse/keyboard working in Windows
- [ ] Python runner can find script
- [ ] Script has read permissions
- [ ] Log file can be written
- [ ] Screen resolution at least 800x600
- [ ] No other fullscreen applications
- [ ] DiagramScene window properly sized

## Next Steps

### 1. **Run Initial Test**
```powershell
python agent/run_autohotkey_tests.py
```

### 2. **Review Results**
```powershell
Get-Content agent/ahk_test_results.json | ConvertFrom-Json
```

### 3. **Debug Failures**
- Identify failed tests
- Adjust coordinates/timing
- Re-run to verify

### 4. **Integrate with Flask**
- Use `autohotkey_integration.py`
- Add to test pipeline
- Display in Flask UI

### 5. **Create Reports**
```powershell
# Generate summary
python agent/run_autohotkey_tests.py --output "test_report.json"
```

## FAQ

**Q: Can I run tests without a GUI?**
A: No, AutoHotkey tests require GUI interaction. Use echo tests for headless/CI environments.

**Q: How long should tests take?**
A: Typically 40-60 seconds for all 22 tests.

**Q: Can I run tests in parallel?**
A: Not recommended - DiagramScene window conflicts. Run sequentially.

**Q: What if DiagramScene crashes?**
A: Script includes crash detection. Check logs and adjust timing.

**Q: How do I know which test failed?**
A: Check `ahk_test_results.json` for detailed status and timestamps.

## References

- AutoHotkey Documentation: https://www.autohotkey.com/docs/
- AutoHotkey v2.0 API: https://www.autohotkey.com/docs/v2/
- DiagramScene Project: [Your project location]
- Test Cases Reference: TEST_CASES_DIAGRAMSCENE.md

---

**Last Updated:** 2024
**Status:** Ready for Production
**Compatibility:** Windows 10+, AutoHotkey v2.0+, DiagramScene with GUI
