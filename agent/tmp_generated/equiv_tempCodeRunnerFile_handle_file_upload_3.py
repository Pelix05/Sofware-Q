import sys
from agent.archive_python_tools_20251124_142656.tempCodeRunnerFile import handle_file_upload
import json
try:
    res = handle_file_upload(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
