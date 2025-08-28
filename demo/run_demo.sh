#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import json, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def run(subj, desc):
    print("\n===== RUN =====")
    print("Subject:", subj)
    print("Description:", desc)
    res = subprocess.run([sys.executable, str(root/"client.py"), "--subject", subj, "--description", desc], capture_output=True, text=True)
    print(res.stdout)

with open(str(root/"demo/tickets.jsonl"), "r", encoding="utf-8") as f:
    for line in f:
        t = json.loads(line)
        run(t["subject"], t["description"])
PY
