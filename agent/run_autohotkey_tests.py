#!/usr/bin/env python3
"""
AutoHotkey Test Runner for DiagramScene
========================================

Runs the AutoHotkey GUI automation tests and integrates results with the test framework.
Provides detailed logging and error handling.

Usage:
    python run_autohotkey_tests.py
    python run_autohotkey_tests.py --script diagramscene_tests.ahk
    python run_autohotkey_tests.py --timeout 300
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class AutoHotKeyTestRunner:
    """Manages AutoHotKey test execution and result parsing."""
    
    def __init__(self, script_path: Optional[str] = None, timeout: int = 600):
        """
        Initialize the test runner.
        
        Args:
            script_path: Path to the AutoHotKey script (auto-detects if None)
            timeout: Maximum execution time in seconds
        """
        self.script_path = Path(script_path) if script_path else self._find_script()
        self.timeout = timeout
        self.log_file = self.script_path.parent / "ahk_test_results.txt"
        self.results: List[Dict] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        
    def _find_script(self) -> Path:
        """Auto-detect diagramscene_tests.ahk location."""
        current_dir = Path(__file__).resolve().parent
        
        # Try v2 script first
        script = current_dir / "diagramscene_tests_v2.ahk"
        if script.exists():
            return script
        
        # Fall back to regular script
        script = current_dir / "diagramscene_tests.ahk"
        if script.exists():
            return script
        
        # Try parent directory
        script = current_dir.parent / "diagramscene_tests.ahk"
        if script.exists():
            return script
        
        raise FileNotFoundError("Could not find diagramscene_tests.ahk or diagramscene_tests_v2.ahk")
    
    def check_autohotkey_installed(self) -> bool:
        """Check if AutoHotkey is installed and accessible."""
        try:
            result = subprocess.run(
                ["where", "AutoHotkey.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error checking AutoHotkey: {e}")
            return False
    
    def run_tests(self) -> Tuple[bool, List[Dict]]:
        """
        Execute the AutoHotkey test script.
        
        Returns:
            Tuple of (success: bool, results: List[Dict])
        """
        print(f"\n{'='*60}")
        print("AutoHotkey Test Runner")
        print(f"{'='*60}\n")
        
        # Check AutoHotkey installation
        if not self.check_autohotkey_installed():
            print("❌ ERROR: AutoHotkey not installed")
            print("   Install from: https://www.autohotkey.com/")
            return False, [{
                "test": "AutoHotkey Environment",
                "status": "SKIPPED",
                "detail": "AutoHotkey not installed"
            }]
        
        # Check script exists
        if not self.script_path.exists():
            print(f"❌ ERROR: Script not found: {self.script_path}")
            return False, [{
                "test": "AutoHotkey Script",
                "status": "FAIL",
                "detail": f"Script not found: {self.script_path}"
            }]
        
        print(f"✓ Script found: {self.script_path}")
        print(f"✓ AutoHotkey installed")
        print(f"✓ Log file: {self.log_file}")
        print(f"✓ Timeout: {self.timeout} seconds")
        print(f"\nLaunching tests...\n")
        
        # Remove old log
        if self.log_file.exists():
            self.log_file.unlink()
        
        # Run the script
        try:
            start_time = time.time()
            
            result = subprocess.run(
                ["AutoHotkey.exe", str(self.script_path)],
                cwd=str(self.script_path.parent),
                timeout=self.timeout,
                capture_output=True,
                text=True
            )
            
            elapsed = time.time() - start_time
            print(f"✓ Tests completed in {elapsed:.1f} seconds")
            
            # Read and parse results
            success, results = self._parse_results()
            return success, results
            
        except subprocess.TimeoutExpired:
            print(f"❌ Tests timed out after {self.timeout} seconds")
            return False, [{
                "test": "AutoHotkey Tests",
                "status": "FAIL",
                "detail": f"Tests timed out after {self.timeout} seconds"
            }]
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False, [{
                "test": "AutoHotkey Tests",
                "status": "FAIL",
                "detail": f"Error: {str(e)}"
            }]
    
    def _parse_results(self) -> Tuple[bool, List[Dict]]:
        """Parse test results from log file."""
        if not self.log_file.exists():
            return False, [{
                "test": "AutoHotkey Tests",
                "status": "FAIL",
                "detail": "Log file not created"
            }]
        
        try:
            content = self.log_file.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            return False, [{
                "test": "AutoHotkey Tests",
                "status": "FAIL",
                "detail": f"Could not read log file: {e}"
            }]
        
        # Parse each test result
        results = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('=') or line.startswith('>'):
                continue
            
            # Parse test result lines
            if '✓ PASS' in line:
                test_name = line.split('[')[0].strip() if '[' in line else line.split('✓')[0].strip()
                results.append({
                    "test": test_name,
                    "status": "PASS",
                    "detail": test_name
                })
                self.passed += 1
            elif '✗ FAIL' in line or '✗ ERROR' in line:
                test_name = line.split('[')[0].strip() if '[' in line else line.split('✗')[0].strip()
                detail = line.split('-')[-1].strip() if '-' in line else ""
                results.append({
                    "test": test_name,
                    "status": "FAIL",
                    "detail": detail or test_name
                })
                self.failed += 1
        
        # Print summary
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        print("Test Results Summary")
        print(f"{'='*60}")
        print(f"  Total:  {total}")
        print(f"  Passed: {self.passed} ✓")
        print(f"  Failed: {self.failed} ✗")
        print(f"  Skipped: {self.skipped} ⊘")
        print(f"{'='*60}\n")
        
        success = self.failed == 0
        
        if results:
            print("Individual Results:")
            for r in results:
                status_icon = "✓" if r['status'] == "PASS" else "✗"
                print(f"  {status_icon} {r['test']}: {r['status']}")
        
        return success, results if results else [{
            "test": "AutoHotkey Tests",
            "status": "FAIL",
            "detail": "No results parsed"
        }]
    
    def save_results(self, output_file: Optional[str] = None) -> str:
        """
        Save results to JSON file.
        
        Args:
            output_file: Output file path (default: ahk_test_results.json)
        
        Returns:
            Path to saved file
        """
        if not output_file:
            output_file = self.script_path.parent / "ahk_test_results.json"
        
        output_path = Path(output_file)
        data = {
            "timestamp": datetime.now().isoformat(),
            "script": str(self.script_path),
            "results": self.results,
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "skipped": self.skipped,
                "total": self.passed + self.failed + self.skipped
            }
        }
        
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"\n✓ Results saved to: {output_path}\n")
        return str(output_path)


def main():
    """Main entry point."""
    import argparse
    
    # Fix Unicode output on Windows
    import io
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(
        description="Run AutoHotkey tests for DiagramScene"
    )
    parser.add_argument(
        "--script",
        help="Path to AutoHotkey test script",
        default=None
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Test timeout in seconds (default: 600)"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        runner = AutoHotKeyTestRunner(args.script, args.timeout)
        success, results = runner.run_tests()
        runner.results = results
        
        if args.output:
            runner.save_results(args.output)
        else:
            runner.save_results()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
