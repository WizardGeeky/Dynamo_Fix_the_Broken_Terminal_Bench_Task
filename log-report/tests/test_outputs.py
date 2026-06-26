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
    """1. It contains a "total_requests" key with the integer total number of requests found in the log."""
    assert "total_requests" in report, "missing total_requests key"
    assert isinstance(report["total_requests"], int), "total_requests must be an integer"
    assert report["total_requests"] == 6, f"total_requests should be 6, got {report['total_requests']}"

def test_criterion_2(report):
    """2. It contains a "unique_ips" key with the integer count of unique client IP addresses."""
    assert "unique_ips" in report, "missing unique_ips key"
    assert isinstance(report["unique_ips"], int), "unique_ips must be an integer"
    assert report["unique_ips"] == 3, f"unique_ips should be 3, got {report['unique_ips']}"

def test_criterion_3(report):
    """3. It contains a "top_path" key with the string path of the most requested URI."""
    assert "top_path" in report, "missing top_path key"
    assert isinstance(report["top_path"], str), "top_path must be a string"
    assert report["top_path"] == "/index.html", f"top_path should be /index.html, got {report['top_path']}"
