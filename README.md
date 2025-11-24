# AI Agent Project — Build & Run Guide

This repository contains an agent used for automated static and dynamic analysis of student projects (C++ Qt and Python puzzles).

This README documents how to make the Flask UI able to compile C++ Qt projects when uploaded, and the environment variables the agent uses.

## Required tools (example tested configuration)
- Windows 10/11
- MSYS2 MinGW-w64 (mingw64) — provides `g++` and `mingw32-make`.
- Qt 6.9.2 (MinGW 64-bit kit) — qt bin (qmake, moc) and the Qt Multimedia/Sql modules.
- Python 3.8+ for the agent scripts.

Example installation paths used in the project:
- `C:\msys64\mingw64\bin`
- `C:\Qt\6.9.2\mingw_64\bin`

## Environment variables (recommended)
You can create a file `agent/.env` with the following keys, or set them system-wide before starting the Flask app:

```
# Example agent/.env
QT_INCLUDES=C:\Qt\6.9.2\mingw_64\include
QT_LIBS=C:\Qt\6.9.2\mingw_64\lib
MSYS2_PATH=C:\msys64\mingw64\bin
QT_BIN_PATH=C:\Qt\6.9.2\mingw_64\bin
```

The Flask background worker will read `agent/.env` (if present) and propagate these to the `dynamic_tester.py` invocation.

## Starting the Flask UI (PowerShell)
Open PowerShell and (optionally) set PATH for the session, then start the Flask app:

```powershell
$env:PATH = 'C:\msys64\mingw64\bin;C:\Qt\6.9.2\mingw_64\bin;' + $env:PATH
python agent\FlaskApp.py
```

## If compilation fails on upload
- Ensure the Qt modules used by the project (Widgets, Multimedia, Sql) are installed in your Qt kit.
- Make sure `qmake`, `moc`, `g++`, and `mingw32-make` are on `PATH` for the Flask process.
- If the server has low memory, the agent disables sanitizers for background runs (no extra action needed). If you want sanitizers locally, run `dynamic_tester.py` directly and unset `DYNAMIC_TESTER_NO_SANITIZERS`.

## CI suggestion
Add a GitHub Actions workflow to validate builds on push (use MSYS2 or a Qt installer action to setup Qt).

## Notes
- Do not commit generated files (moc_*.cpp, qrc_*.cpp, release/, debug/). Use `.gitignore` to prevent accidental commits.
- The agent is intentionally non-destructive for Experiment 2: it analyzes projects but does not apply code patches.
