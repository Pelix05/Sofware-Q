GoogleTest integration for white-box C++ tests

Build & run (recommended: use a developer shell with MinGW or a system with CMake + make)

Windows (PowerShell, MinGW)

```powershell
# from repo root
cd agent/cpp_tests
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build -j 4
ctest --test-dir build --output-on-failure
```

Linux/macOS

```bash
cd agent/cpp_tests
cmake -S . -B build
cmake --build build -j4
ctest --test-dir build --output-on-failure
```

Notes
- This CMakeLists uses FetchContent to download GoogleTest at configure time so no external package manager is required.
- For CI, cache the googletest sources or vendor them into the repo for reproducible builds.
- Extend `tests/` with tests for actual project code and adjust include paths as needed.

Sanitizers
---------
You can build the tests with AddressSanitizer and UndefinedBehaviorSanitizer (recommended on Linux/macOS) by enabling the CMake option:

```powershell
cd agent/cpp_tests
cmake -S . -B build -DUSE_SANITIZERS=ON
cmake --build build -j 4
ctest --test-dir build --output-on-failure
```

Notes:
- Sanitizers require a compatible toolchain (GCC/Clang). They are not fully supported with MSVC on Windows.
- When running with sanitizers you may need to set environment variables to control sanitizer behavior, e.g.:
	- `export ASAN_OPTIONS=detect_leaks=1:abort_on_error=1` (Linux/macOS)
	- On CI, prefer Ubuntu runners with Clang or GCC for sanitizer-enabled jobs.
