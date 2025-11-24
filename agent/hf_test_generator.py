import os
import json
import requests
from pathlib import Path


def _load_env_file(env_path: Path):
    """Load simple KEY=VALUE pairs from an env file into os.environ if not already set."""
    try:
        txt = env_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"\'')
        if k and v and k not in os.environ:
            os.environ[k] = v


def _summarize_repo(repo_path: Path, max_files=30):
    """Collect a short summary of the repo: README (first N chars) and file list."""
    repo = Path(repo_path)
    summary = {}
    readme_text = ""
    for name in ("README.md", "README.rst", "README.txt"):
        f = repo / name
        if f.exists():
            try:
                readme_text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                readme_text = ""
            break
    files = []
    for p in sorted(repo.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(repo)).replace('\\', '/')
            files.append(rel)
            if len(files) >= max_files:
                break
    summary['readme'] = (readme_text[:4000] + '...') if readme_text and len(readme_text) > 4000 else readme_text
    summary['files'] = files
    # additional signals to help HF prompt
    summary['qrc'] = [f for f in files if f.lower().endswith('.qrc')]
    summary['ui'] = [f for f in files if f.lower().endswith('.ui')]
    summary['pro'] = [f for f in files if f.lower().endswith('.pro')]
    # scan a few header files for Q_OBJECT macro
    qobj = []
    for suf in ('.h', '.hpp', '.hh'):
        for p in repo.rglob(f'*{suf}'):
            try:
                txt = p.read_text(encoding='utf-8', errors='ignore')
                if 'Q_OBJECT' in txt:
                    rel = str(p.relative_to(repo)).replace('\\', '/')
                    qobj.append(rel)
            except Exception:
                continue
            if len(qobj) >= 10:
                break
        if len(qobj) >= 10:
            break
    summary['qobject_headers'] = qobj
    # guess likely executable names
    summary['likely_exes'] = []
    if any('main.cpp' in f.lower() for f in files):
        summary['likely_exes'].append('main.exe')
    summary['likely_exes'].append('release\\app.exe')
    return summary


def _build_prompt(summary: dict, language: str = 'cpp'):
    """Construct the prompt asking the HF model to generate test cases in JSON.
    Output format: JSON array of objects: {"name","short","commands","expected"}
    """
    readme = summary.get('readme') or ''
    files = summary.get('files') or []
    qrc = summary.get('qrc') or []
    ui = summary.get('ui') or []
    pro = summary.get('pro') or []
    qobj = summary.get('qobject_headers') or []
    exes = summary.get('likely_exes') or []

    example = (
        '[\n'
        '  {"name":"run_app","title":"Start app","description":"Start the built application and ensure it launches","commands":["./release/app.exe"],"expected":"Process starts without crash and returns 0 or GUI shows main window"},\n'
        '  {"name":"load_resources","title":"Load resources","description":"Ensure qrc resources load","commands":["# run and check stdout/stderr for resource load messages"],"expected":"No missing resource errors"}\n'
        ']'
    )

    prompt = (
        "You are a concise QA assistant that generates small, runnable test-case descriptions for C/C++ projects (Qt allowed).\n"
        "Return ONLY valid JSON: an array of objects. Each object must contain the fields: name, title, description, commands (array), expected.\n"
        "Produce 3-8 focused test cases tailored to the project. Prefer non-GUI checks but include at least one runtime start test and one resource check if resources exist.\n\n"
        "EXAMPLE OUTPUT (JSON only):\n" + example + "\n\n"
        "Project README (truncated):\n" + (readme[:2000] if readme else "<no readme>") + "\n\n"
        "Top files in project:\n" + ("\n".join(files[:40]) if files else "<no files>") + "\n\n"
        "Project signals:\n"
        f"- qrc_files: {', '.join(qrc) if qrc else '<none>'}\n"
        f"- ui_files: {', '.join(ui) if ui else '<none>'}\n"
        f"- pro_files: {', '.join(pro) if pro else '<none>'}\n"
        f"- headers_with_Q_OBJECT: {', '.join(qobj[:10]) if qobj else '<none>'}\n"
        f"- likely_exec_names: {', '.join(exes)}\n\n"
        "Return JSON only. If unsure, prefer safe tests (README/build checks) rather than speculative runtime tests."
    )
    return prompt


def _call_hf_api(prompt: str, model: str, token: str, timeout=60, temperature=0.2):
    """Call Hugging Face Router. Prefer the OpenAI-compatible v1 chat completions endpoint.
    Returns generated text (string) or an error payload string for debugging.
    """
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # First, try the OpenAI-compatible chat completions endpoint on the router
    chat_url = "https://router.huggingface.co/v1/chat/completions"
    chat_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 512,
    }
    try:
        resp = requests.post(chat_url, headers=headers, json=chat_payload, timeout=timeout)
        # prefer structured chat completion response
        try:
            j = resp.json()
            # typical shape: {choices: [{message: {role:..., content: ...}}], ...}
            if isinstance(j, dict) and 'choices' in j and isinstance(j['choices'], list) and len(j['choices']) > 0:
                first = j['choices'][0]
                # support both chat style and text style
                if isinstance(first, dict) and 'message' in first and isinstance(first['message'], dict):
                    return first['message'].get('content') or json.dumps(first)
                if isinstance(first, dict) and 'text' in first:
                    return first['text']
            # if router returns an error dict
            if isinstance(j, dict) and 'error' in j:
                return json.dumps(j)
            return resp.text
        except Exception:
            return resp.text
    except Exception:
        # fallback: try the older /models/<id> inference endpoints
        try:
            urls_to_try = [
                f"https://api-inference.huggingface.co/models/{model}",
                f"https://router.huggingface.co/models/{model}",
            ]
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 512, "temperature": temperature}}
            resp = None
            for url in urls_to_try:
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                except Exception:
                    resp = None
                if resp is None:
                    continue
            if resp is None:
                return "ERROR: no response from HF endpoints"
            try:
                j = resp.json()
                if isinstance(j, dict) and 'generated_text' in j:
                    return j['generated_text']
                if isinstance(j, list):
                    txts = []
                    for it in j:
                        if isinstance(it, dict) and 'generated_text' in it:
                            txts.append(it['generated_text'])
                    if txts:
                        return '\n'.join(txts)
                    return json.dumps(j)
                if isinstance(j, dict) and 'error' in j:
                    return json.dumps(j)
                return resp.text
            except Exception:
                return resp.text
        except Exception as e:
            import traceback
            return traceback.format_exc()


def _call_ollama(host: str, model: str, prompt: str, timeout: int = 60, temperature: float = 0.0):
    """Call a local Ollama server. Returns the generated text or error string."""
    try:
        url = host.rstrip('/') + '/api/generate'
        payload = {
            'model': model,
            'prompt': prompt,
            'max_tokens': 512,
            'temperature': temperature,
        }
        resp = requests.post(url, json=payload, timeout=timeout)
        try:
            j = resp.json()
            # Ollama returns {'generated': '...', ' ...'} or sometimes {'responses':[...]} depending on version
            if isinstance(j, dict):
                if 'generated' in j:
                    return j['generated']
                if 'responses' in j and isinstance(j['responses'], list) and j['responses']:
                    r0 = j['responses'][0]
                    if isinstance(r0, dict) and 'content' in r0:
                        return r0['content']
                    return str(r0)
            return resp.text
        except Exception:
            return resp.text
    except Exception as e:
        import traceback
        return traceback.format_exc()


def generate_tests(workspace_path: str, repo_path: str = None, model: str = None, token: str = None):
    """Generate test cases for repo_path, write generated_tests.json into workspace_path and return list.

    If HF API token or model missing, return a small heuristic set.
    """
    ws = Path(workspace_path)
    repo = Path(repo_path) if repo_path else ws
    summary = _summarize_repo(repo)
    prompt = _build_prompt(summary)

    # model and token: prefer passed args then env; if missing try common HF env names and nearby .env files
    def _env_any(keys):
        for k in keys:
            v = os.environ.get(k)
            if v:
                return v
        return None

    hf_model = model or _env_any(['HF_MODEL_ID', 'HUGGINGFACE_MODEL_ID', 'HUGGINGFACE_ROUTER_MODEL', 'HUGGINGFACE_MODEL_URL'])
    hf_token = token or _env_any(['HF_API_TOKEN', 'HUGGINGFACE_API_TOKEN'])

    if (not hf_model or not hf_token) and repo:
        # look for .env in repo and ancestors (up to 6 levels)
        repo_p = Path(repo)
        cur = repo_p
        for _ in range(6):
            c = cur / '.env'
            if c.exists():
                _load_env_file(c)
            if not cur.parent or cur.parent == cur:
                break
            cur = cur.parent
        # re-read after loading using same env name checks
        hf_model = hf_model or _env_any(['HF_MODEL_ID', 'HUGGINGFACE_MODEL_ID', 'HUGGINGFACE_ROUTER_MODEL', 'HUGGINGFACE_MODEL_URL'])
        hf_token = hf_token or _env_any(['HF_API_TOKEN', 'HUGGINGFACE_API_TOKEN'])

    generated = None
    raw_hf = None
    if hf_model and hf_token:
        # Try a couple of temperatures to favor valid JSON output
        for temp in (0.2, 0.0):
            # call HF inference
            raw = _call_hf_api(prompt, hf_model, hf_token)
            raw_hf = raw or raw_hf
            if not raw:
                continue
            # try to extract JSON array
            import re
            m = re.search(r"(\[\s*\{.*?\}\s*\])", raw, flags=re.S)
            if m:
                try:
                    generated = json.loads(m.group(1))
                    break
                except Exception:
                    generated = None
            else:
                try:
                    generated = json.loads(raw)
                    break
                except Exception:
                    generated = None

    # Log raw HF output to workspace for debugging
    try:
        if raw_hf:
            (ws / 'generated_tests_debug.txt').write_text(raw_hf, encoding='utf-8')
    except Exception:
        pass

    # If HF didn't produce output and Ollama is configured, try Ollama
    if not generated:
        ollama_host = os.environ.get('OLLAMA_HOST')
        ollama_model = os.environ.get('LOCAL_MODEL') or os.environ.get('OLLAMA_MODEL')
        if ollama_host and ollama_model:
            try:
                ollama_out = _call_ollama(ollama_host, ollama_model, prompt, timeout=int(os.environ.get('OLLAMA_TIMEOUT', 60)))
                if ollama_out:
                    # try to extract a JSON array
                    import re
                    m = re.search(r"(\[\s*\{.*?\}\s*\])", ollama_out, flags=re.S)
                    if m:
                        try:
                            generated = json.loads(m.group(1))
                        except Exception:
                            generated = None
                    else:
                        try:
                            generated = json.loads(ollama_out)
                        except Exception:
                            generated = None
                    # save raw Ollama output for debugging
                    try:
                        (ws / 'generated_tests_ollama_debug.txt').write_text(str(ollama_out), encoding='utf-8')
                    except Exception:
                        pass
            except Exception:
                pass

    if not generated:
        # fallback heuristic generator: create tests tailored by repo signals
        gen = []
        files = summary.get('files') or []
        qrc = summary.get('qrc') or []
        pro = summary.get('pro') or []
        qobj = summary.get('qobject_headers') or []
        exes = summary.get('likely_exes') or ['main.exe', 'release\\app.exe']

        likely_exe = exes[0] if exes else 'main.exe'

        # runtime start test
        gen.append({
            "name": "run_executable",
            "title": "Start executable",
            "description": "Start the built executable and ensure it launches.",
            "commands": [f"# build if needed - try qmake/make if present\nif exist release\\*.exe ({likely_exe}) else echo 'no executable'"],
            "expected": "Process starts without crash or shows main window; no immediate crash messages in stderr"
        })

        # resource loading check (only if qrc present)
        if qrc:
            gen.append({
                "name": "resource_load",
                "title": "Resource loading check",
                "description": "Verify that embedded qrc resources (images/sounds) are accessible at runtime.",
                "commands": ["# run the app and inspect stdout/stderr for resource load messages or run a small loader"],
                "expected": "No missing resource errors; resources accessible"
            })

        # README presence test
        gen.append({
            "name": "readme_exists",
            "title": "README present",
            "description": "Check project README for build/run instructions.",
            "commands": ["type README.md || type README.txt || echo 'no readme'"],
            "expected": "README present and contains 'build' or 'run' sections"
        })
        generated = gen

    # write to workspace
    try:
        outp = ws / 'generated_tests.json'
        outp.write_text(json.dumps(generated, indent=2, ensure_ascii=False), encoding='utf-8')
    except Exception:
        pass

    return generated


if __name__ == '__main__':
    import sys
    wp = sys.argv[1] if len(sys.argv) > 1 else '.'
    rp = sys.argv[2] if len(sys.argv) > 2 else wp
    print(generate_tests(wp, rp))
