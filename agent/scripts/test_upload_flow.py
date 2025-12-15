import io
import os
import sys
import time
import zipfile
from pathlib import Path

# Ensure we can import the Flask app
sys.path.append(str(Path(__file__).resolve().parents[1]))
from FlaskApp import app

ZIP_PATH = Path(__file__).resolve().parents[1] / 'temp_upload.zip'

# Create a minimal C++ project to upload (avoid nested build artifacts)
tmpdir = Path(__file__).resolve().parents[1] / 'upload_tmp'
if tmpdir.exists():
    try:
        import shutil
        shutil.rmtree(tmpdir)
    except Exception:
        pass
tmpdir.mkdir(parents=True, exist_ok=True)
src_dir = tmpdir / 'cpp_project'
src_dir.mkdir(parents=True, exist_ok=True)
main_cpp = src_dir / 'main.cpp'
cmake = src_dir / 'CMakeLists.txt'
main_cpp.write_text('''#include <iostream>\nint main(){ std::cout<<"hello"<<std::endl; return 0; }\n''', encoding='utf-8')
cmake.write_text('''cmake_minimum_required(VERSION 3.0)\nproject(upload_test)\nadd_executable(upload_test main.cpp)\n''', encoding='utf-8')

with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for p in src_dir.rglob('*'):
        if p.is_file():
            arc = p.relative_to(tmpdir)
            zf.write(p, arcname=str(arc))

print('Created zip:', ZIP_PATH)

# Use Flask test client to post file
client = app.test_client()
with open(ZIP_PATH, 'rb') as f:
    data = {
        'file': (io.BytesIO(f.read()), 'upload.zip'),
        'file_type': 'cpp'
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')

print('Upload response status:', resp.status_code)
print(resp.get_data(as_text=True))
try:
    j = resp.get_json()
except Exception:
    j = None
if not j or j.get('status') != 'Accepted':
    print('Upload not accepted, aborting')
    sys.exit(1)
ws = j.get('workspace')
print('Workspace id returned:', ws)

# Poll status until done
for i in range(60):
    st = client.get('/status', query_string={'ws': ws})
    try:
        sj = st.get_json()
    except Exception:
        sj = None
    print('Status poll', i, '->', sj.get('status') if sj else st.status_code)
    if sj and sj.get('status') in ('Done', 'done', 'Complete', 'complete'):
        res = sj.get('result') if sj.get('result') else sj
        print('Final result keys:', list(res.keys()) if isinstance(res, dict) else type(res))
        if isinstance(res, dict):
            print('generated_tests present:', 'generated_tests' in res)
            print('generated_tests_path present:', 'generated_tests_path' in res)
            if 'generated_tests' in res and isinstance(res['generated_tests'], list):
                print('Number of generated tests:', len(res['generated_tests']))
        break
    time.sleep(1)
else:
    print('Timeout waiting for workspace processing')

# cleanup
try:
    os.remove(ZIP_PATH)
except Exception:
    pass
