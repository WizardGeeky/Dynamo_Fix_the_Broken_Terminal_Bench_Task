# 📊 dynamo/log-report — Terminal-Bench 2 Task

> **Task Name:** `dynamo/log-report`  
> **Category:** Data Processing & ETL → Text Processing  
> **Difficulty:** Easy  
> **Estimated Expert Time:** ~18 minutes  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Task Instruction](#task-instruction)
3. [Project Structure](#project-structure)
4. [Input Data](#input-data)
5. [Expected Output](#expected-output)
6. [Defects Found (Original Broken Task)](#defects-found-original-broken-task)
7. [Fixes Applied](#fixes-applied)
8. [File-by-File Changes](#file-by-file-changes)
9. [How the Solution Works](#how-the-solution-works)
10. [How the Verifier Works](#how-the-verifier-works)
11. [Verifier Evidence](#verifier-evidence)
12. [Running Locally](#running-locally)
13. [Environment Details](#environment-details)

---

## Overview

This is a **Terminal-Bench 2 (Harbor)** task that tests whether an AI agent can parse an Apache-style HTTP access log and produce a structured JSON summary report.

The task was originally **broken** with 5 distinct defects spanning the configuration format, Docker environment, verifier logic, and output paths. This README documents every defect found, every fix applied, and provides verifier evidence for correctness.

---

## Task Instruction

> There is an access log at `/app/access.log`. Analyze the traffic and summarize what you find.  
> Please write your findings to `/app/report.json` in JSON format.
>
> Your JSON report must satisfy the following criteria:
> 1. It contains a `"total_requests"` key with the **integer** total number of requests found in the log.
> 2. It contains a `"unique_ips"` key with the **integer** count of unique client IP addresses.
> 3. It contains a `"top_path"` key with the **string** path of the most requested URI.

---

## Project Structure

```
log-report/
├── instruction.md          # Task prompt shown to the agent
├── task.toml               # Harbor task configuration (format, metadata, verifier, environment)
│
├── environment/
│   ├── Dockerfile          # Builds the sandbox container (pinned base image)
│   └── access.log          # Input: Apache-style HTTP access log (6 lines)
│
├── solution/
│   ├── solve.py            # Oracle solution (Python script)
│   └── solve.sh            # Oracle entry point (calls solve.py)
│
└── tests/
    ├── test.sh             # Verifier entry point (runs pytest, writes reward + ctrf)
    └── test_outputs.py     # pytest test file (3 tests, checks exact values)
```

---

## Input Data

**`environment/access.log`** — 6 valid Apache-style log lines:

```
192.168.0.1 - - [16/Jun/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 1024
192.168.0.2 - - [16/Jun/2026:10:00:02 +0000] "GET /about.html HTTP/1.1" 200 512
192.168.0.1 - - [16/Jun/2026:10:00:03 +0000] "GET /index.html HTTP/1.1" 200 1024
10.0.0.5   - - [16/Jun/2026:10:00:04 +0000] "POST /api/login HTTP/1.1" 401 64
192.168.0.2 - - [16/Jun/2026:10:00:05 +0000] "GET /index.html HTTP/1.1" 200 1024
10.0.0.5   - - [16/Jun/2026:10:00:06 +0000] "GET /about.html HTTP/1.1" 200 512
```

| Metric | Value |
|--------|-------|
| Total requests | **6** |
| Unique IPs | **3** (`192.168.0.1`, `192.168.0.2`, `10.0.0.5`) |
| Top path | **`/index.html`** (hit 3 times) |

---

## Expected Output

The agent must write `/app/report.json` with exactly this structure:

```json
{
  "total_requests": 6,
  "unique_ips": 3,
  "top_path": "/index.html"
}
```

---

## Defects Found (Original Broken Task)

Five real defects were present across the task. Two options in the assessment were traps (not real defects).

### ✅ Defect 1 — `task.toml`: `artifacts` is a string, not an array

| | Detail |
|---|---|
| **File** | `task.toml` |
| **Broken value** | `artifacts = "/app/report.json"` |
| **Required value** | `artifacts = ["/app/report.json"]` |
| **Impact** | Harbor cannot parse the field correctly; artifact collection silently fails or raises a schema error |

---

### ✅ Defect 2 — `environment/Dockerfile`: Unpinned base image

| | Detail |
|---|---|
| **File** | `environment/Dockerfile` |
| **Broken value** | `FROM python:3.12-slim-bookworm` |
| **Required value** | `FROM python:3.12-slim-bookworm@sha256:<digest>` |
| **Impact** | Builds are non-reproducible; Docker Hub may silently update the image between runs, producing different OS-level behaviour |

---

### ✅ Defect 3 — Agent image leaks the reference solution

| | Detail |
|---|---|
| **File** | `environment/Dockerfile` (build context) |
| **Broken behaviour** | `solution/solve.py` was accessible inside the agent container |
| **Impact** | The agent could read and copy the oracle answer directly — the task is trivially gameable without any reasoning |

---

### ✅ Defect 4 — Verifier is gameable (checks file exists, not values)

| | Detail |
|---|---|
| **File** | `tests/test_outputs.py` |
| **Broken behaviour** | Only verified `report.json` exists and is a JSON dict |
| **What would pass it** | `{}`, `{"total_requests": 0}`, any valid JSON object |
| **Impact** | An agent that writes an empty file scores `reward=1`; correctness is never tested |

---

### ✅ Defect 5 — `test.sh` writes reward to wrong path and omits `ctrf.json`

| | Detail |
|---|---|
| **File** | `tests/test.sh` |
| **Broken** | Wrote to `/reward.txt`; no `--ctrf` flag passed to pytest |
| **Required** | `/logs/verifier/reward.txt` and `/logs/verifier/ctrf.json` |
| **Impact** | Harbor reads reward from a fixed path. Wrong path = no reward signal detected = all runs appear to score 0 |

---

### ❌ NOT a defect — `instruction.md` ambiguity (trap option)

The instruction clearly and consistently lists all 3 required output keys in exact alignment with the verifier assertions. No ambiguity exists.

### ❌ NOT a defect — `access.log` is corrupted (trap option)

The log file is valid and well-formed. The oracle correctly parses it to produce the expected values.

---

## Fixes Applied

### Fix 1 — `task.toml`

```diff
- artifacts = "/app/report.json"
+ artifacts = ["/app/report.json"]

- allow_internet = true
+ allow_internet = false
```

### Fix 2 — `environment/Dockerfile`

```diff
- FROM python:3.12-slim-bookworm
+ FROM python:3.12-slim-bookworm@sha256:8a7e7cc04fd3e2bd787f7f24e22d5d119aa590d429b50c95dfe12b3abe52f48b

  RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

  WORKDIR /app
  COPY access.log /app/access.log
+ # solution/ is NOT copied — excluded from build context
```

### Fix 3 — `tests/test_outputs.py`

```diff
- def test_report_exists():
-     assert report_path.exists()
-     data = json.load(open(report_path))
-     assert isinstance(data, dict)

+ def test_total_requests():
+     report = get_report()
+     assert "total_requests" in report
+     assert report["total_requests"] == 6
+
+ def test_unique_ips():
+     report = get_report()
+     assert "unique_ips" in report
+     assert report["unique_ips"] == 3
+
+ def test_top_path():
+     report = get_report()
+     assert "top_path" in report
+     assert report["top_path"] == "/index.html"
```

### Fix 4 — `tests/test.sh`

```diff
- pytest /tests/test_outputs.py
- echo $? > /reward.txt

+ mkdir -p /logs/verifier
+ pytest /tests/test_outputs.py -rA --json-ctrf /logs/verifier/ctrf.json
+ if [ $? -eq 0 ]; then
+   echo 1 > /logs/verifier/reward.txt
+ else
+   echo 0 > /logs/verifier/reward.txt
+ fi
```

---

## File-by-File Changes

### `task.toml` (final corrected file)

```toml
artifacts = ["/app/report.json"]

[task]
name = "dynamo/log-report"
description = "Parse an Apache-style access log into a small JSON summary report."

[metadata]
category = "data_processing_and_etl"
subcategory = "text_processing"
task_objective = ["transform", "generate"]
artifact_type = ["text_or_log_file", "generated_output_artifact"]
expert_time_estimate_hours = 0.3
model_tested = "GPT-5.4"
agent_tested = "Terminus-2"
difficulty_explanation = "Parse a small access log and emit summary stats."
solution_explanation = "Read the log, count requests/unique IPs, find the top path."
verification_explanation = "Check the report file contains correct computed values."

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 120.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
allow_internet = false
mcp_servers = []
```

---

### `environment/Dockerfile` (final corrected file)

```dockerfile
FROM python:3.12-slim-bookworm@sha256:8a7e7cc04fd3e2bd787f7f24e22d5d119aa590d429b50c95dfe12b3abe52f48b

RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY access.log /app/access.log
```

---

### `tests/test_outputs.py` (final corrected file)

```python
import json
from pathlib import Path
import pytest

@pytest.fixture(scope="module")
def report():
    report_file = Path("/app/report.json")
    assert report_file.exists(), "report.json does not exist"
    try:
        data = json.loads(report_file.read_text())
    except json.JSONDecodeError:
        pytest.fail("report.json is not valid JSON")
    assert isinstance(data, dict), "report.json must contain a JSON object"
    return data

def test_criterion_1(report):
    """total_requests must equal the exact number of log lines."""
    assert "total_requests" in report, "missing total_requests key"
    assert isinstance(report["total_requests"], int), "total_requests must be an integer"
    assert report["total_requests"] == 6, f"total_requests should be 6, got {report['total_requests']}"

def test_criterion_2(report):
    """unique_ips must equal the exact count of distinct client IPs."""
    assert "unique_ips" in report, "missing unique_ips key"
    assert isinstance(report["unique_ips"], int), "unique_ips must be an integer"
    assert report["unique_ips"] == 3, f"unique_ips should be 3, got {report['unique_ips']}"

def test_criterion_3(report):
    """top_path must be the most-requested URI string."""
    assert "top_path" in report, "missing top_path key"
    assert isinstance(report["top_path"], str), "top_path must be a string"
    assert report["top_path"] == "/index.html", f"top_path should be /index.html, got {report['top_path']}"
```

---

### `tests/test.sh` (final corrected file)

```bash
#!/bin/bash

# pytest is baked into the environment image (environment/Dockerfile).
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -rA --json-ctrf /logs/verifier/ctrf.json

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

---

## How the Solution Works

**`solution/solve.py`** — Oracle reference implementation:

```python
import json
import re
from collections import Counter

paths, ips, total = Counter(), set(), 0
with open("/app/access.log") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        total += 1
        ips.add(line.split()[0])                            # first token = IP
        m = re.search(r'"(?:GET|POST|PUT|DELETE|HEAD|PATCH) (\S+) ', line)
        if m:
            paths[m.group(1)] += 1                          # extract URI path

with open("/app/report.json", "w") as out:
    json.dump(
        {
            "total_requests": total,
            "unique_ips": len(ips),
            "top_path": paths.most_common(1)[0][0],
        },
        out,
    )
```

| Step | Logic |
|------|-------|
| Count lines | Each non-empty line = 1 request |
| Unique IPs | Add `line.split()[0]` (first token) to a `set()` |
| Top path | Regex extracts the URI; `Counter.most_common(1)` finds the winner |

---

## How the Verifier Works

The verifier runs **3 independent pytest test functions**, each checking one key in `report.json`:

| Test | Assertion | Expected |
|------|-----------|----------|
| `test_criterion_1` | `report["total_requests"] == 6` | Integer `6` |
| `test_criterion_2` | `report["unique_ips"] == 3` | Integer `3` |
| `test_criterion_3` | `report["top_path"] == "/index.html"` | String `"/index.html"` |

- All 3 pass → `reward.txt = 1`
- Any failure → `reward.txt = 0`
- Results are also written to `ctrf.json` (CTRF format) for Harbor's run report UI.

---

## Verifier Evidence

### ✅ Run 1: `-a oracle` → reward = 1

```
PASSED  tests/test_outputs.py::test_criterion_1   [ 33%]
PASSED  tests/test_outputs.py::test_criterion_2   [ 66%]
PASSED  tests/test_outputs.py::test_criterion_3   [100%]

3 passed in 0.01s
```

`/logs/verifier/reward.txt`:
```
1
```

`/logs/verifier/ctrf.json` summary:
```json
{ "summary": { "tests": 3, "passed": 3, "failed": 0, "skipped": 0 } }
```

---

### ❌ Run 2: `--agent nop` → reward = 0

No file written by the agent. All 3 tests fail at file-existence check.

```
FAILED  test_criterion_1  —  AssertionError: report.json does not exist
FAILED  test_criterion_2  —  AssertionError: report.json does not exist
FAILED  test_criterion_3  —  AssertionError: report.json does not exist

3 failed in 0.02s
```

`/logs/verifier/reward.txt`:
```
0
```

`/logs/verifier/ctrf.json` summary:
```json
{ "summary": { "tests": 3, "passed": 0, "failed": 3, "skipped": 0 } }
```

---

### ❌ Run 3: Bugged solution → reward = 0

Bugged `solve.py` writes intentionally wrong values:
```python
json.dump({
    "total_requests": 99,        # real: 6
    "unique_ips": 1,             # real: 3
    "top_path": "/wrong.html"    # real: /index.html
}, out)
```

```
FAILED  test_criterion_1  —  AssertionError: total_requests should be 6, got 99
FAILED  test_criterion_2  —  AssertionError: unique_ips should be 3, got 1
FAILED  test_criterion_3  —  AssertionError: top_path should be /index.html, got /wrong.html

3 failed in 0.01s
```

`/logs/verifier/reward.txt`:
```
0
```

`/logs/verifier/ctrf.json` summary:
```json
{ "summary": { "tests": 3, "passed": 0, "failed": 3, "skipped": 0 } }
```

---

## Running Locally

> **Prerequisites:** Python 3.12+, `pytest`, `pytest-json-ctrf`

```bash
# 1. Install dependencies
pip install pytest==8.4.1 pytest-json-ctrf==0.3.5

# 2. Run the oracle solution (generates report.json)
python solution/solve.py   # Note: adjust /app/access.log path for local use

# 3. Run the verifier tests
pytest tests/test_outputs.py -v
```

**To simulate all 3 Harbor runs locally:**
```bash
python simulate_runs.py
```

Expected output:
```
oracle  => reward=1  (expect 1) OK
nop     => reward=0  (expect 0) OK
bugged  => reward=0  (expect 0) OK
```

---

## Environment Details

| Setting | Value |
|---------|-------|
| Base image | `python:3.12-slim-bookworm` pinned by `@sha256` |
| Installed packages | `pytest==8.4.1`, `pytest-json-ctrf==0.3.5` |
| Working directory | `/app` |
| Input file | `/app/access.log` |
| Output file | `/app/report.json` |
| CPUs | 1 |
| Memory | 2048 MB |
| Internet access | ❌ Disabled (`allow_internet = false`) |
| GPU | ❌ None |
| MCP servers | ❌ None |
| Verifier timeout | 120 seconds |
| Agent timeout | 120 seconds |
| Build timeout | 600 seconds |
