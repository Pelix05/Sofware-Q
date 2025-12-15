import sys
from agent.archive_python_tools_20251124_142656.python_repo.puzzle-challenge.puzzle_piece import close_enough
import json
try:
    res = close_enough(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
