Refining Static & Dynamic Analysis

This document describes recommended commands and configurations to run static analysis, dynamic analysis, white-box and black-box tests on Windows (PowerShell) and Linux.

1) Python (static)
- Install:
  python -m pip install -r requirements-dev.txt
- Run bandit:
  bandit -r agent/ -lll
- Run flake8:
  flake8 agent/
- Run mypy (optional):
  mypy agent/
- Run semgrep with repo rules:
  semgrep --config .semgrep.yml agent/

2) C/C++ (static)
- Generate a compile_commands.json (CMake usually):
  mkdir -p build && cd build
  cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
- Run clang-tidy (example):
  clang-tidy -p build <source-file>
- Run cppcheck:
  cppcheck --enable=all --inconclusive --std=c++17 --project=build/compile_commands.json

3) Dynamic analysis (C++)
- Preferred: build with sanitizers (Address/UB) and run tests:
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -g -O1" -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address,undefined"
  cmake --build build -j4
  ASAN_OPTIONS=abort_on_error=1:detect_leaks=1:verbosity=1 ./build/myapp

- qmake (Qt projects):
  cd <project-dir-containing-.pro>
  qmake CONFIG+=debug
  mingw32-make -j4

- The `agent/dynamic_tester.py` script tries to auto-detect `.pro` and `CMakeLists.txt` and will run the build in the correct directory. If you see qmake usage/help output, run qmake in the directory containing the `.pro` file.
 - The `agent/dynamic_tester.py` script tries to auto-detect `.pro` and `CMakeLists.txt` and will run the build in the correct directory. If you see qmake usage/help output, run qmake in the directory containing the `.pro` file.
 - You can request sanitizer-enabled builds from `dynamic_tester` with the `--use-sanitizers` flag. Example:
```
py -3 agent\dynamic_tester.py --cpp --cpp-repo agent\workspaces\utnubu__source_20251126_173334\cpp_project --out-dir agent\workspaces\utnubu__source_20251126_173334 --use-sanitizers
```

4) Fuzzing
- Consider libFuzzer or AFL++ depending on platform. Build an instrumented harness accepting input from stdin.

5) White-box tests
- Python: use pytest and coverage. Add unit tests under `agent/` and `agent/tests/`.
  pytest --maxfail=1 -q
  coverage run -m pytest && coverage html
- C++: add GoogleTest targets and include them in CI/build pipelines.
  - C++: add GoogleTest targets and include them in CI/build pipelines.

GTest (C++ white-box)
---------------------
We added a small GoogleTest scaffold under `agent/cpp_tests`.

Build & run (PowerShell, MinGW):
```
cd agent/cpp_tests
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build -j 4
ctest --test-dir build --output-on-failure
```

On Linux/macOS replace the generator with the default and run `cmake -S . -B build` then `cmake --build build`.

The CMakeLists uses `FetchContent` to download GoogleTest at configure time. Extend `agent/cpp_tests/tests/` with unit tests that exercise internal functions and modules for white-box coverage.

6) Black-box / Integration tests
- Use `pytest` with subprocess calls to binaries or HTTP tests for `FlaskApp.py`.
- Example: run `agent/dynamic_tester.py --cpp --cpp-repo <path> --out-dir <out>` to run generated + harness tests for a workspace.

7) Automation
- Add these steps to CI and provide dev environment instructions.
- Windows PowerShell notes: replace shell commands (grep) with `Select-String` or `Get-ChildItem` depending on context.

8) Troubleshooting
- If builds fail with qmake usage help: ensure you ran qmake in the directory that contains the `.pro` file, or pass the full .pro path to qmake. `agent/dynamic_tester.py` will attempt to find `.pro` recursively and run qmake there automatically.

