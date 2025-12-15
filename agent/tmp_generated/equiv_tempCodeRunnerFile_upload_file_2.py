import sys
from agent.archive_python_tools_20251124_142656.tempCodeRunnerFile import upload_file
import json
try:
    res = upload_file(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
