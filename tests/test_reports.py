import json

from app.reports import (
    OperationReport,
    load_latest_report,
    save_csv_report,
    save_json_report,
)


def test_report_finish_sets_completed_at():
    report = OperationReport(operation="scan")
    report.finish()
    assert report.completed_at is not None
    assert report.duration_seconds >= 0.0


def test_report_to_dict_keys():
    report = OperationReport(operation="organization")
    report.finish()
    d = report.to_dict()
    assert "files_scanned" in d
    assert "files_moved" in d
    assert "duplicates" in d
    assert "duration_seconds" in d
    assert "status" in d


def test_add_file_operation():
    report = OperationReport(operation="organization")
    report.add_file_operation(
        original_path="/a/file.jpg",
        destination_path="/a/Images/file.jpg",
        status="MOVED",
    )
    assert len(report.file_operations) == 1
    assert report.file_operations[0].status == "MOVED"


def test_format_summary_contains_fields():
    report = OperationReport(
        operation="organization", files_scanned=100, files_moved=90
    )
    report.finish()
    summary = report.format_summary()
    assert "100" in summary
    assert "90" in summary
    assert "COMPLETED" in summary


def test_save_json_report(tmp_path, monkeypatch):
    monkeypatch.setattr("app.reports.REPORTS_DIR", tmp_path)
    report = OperationReport(operation="scan", files_scanned=50)
    report.finish()
    path = save_json_report(report)
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert data["files_scanned"] == 50
    assert data["operation"] == "scan"


def test_save_csv_report(tmp_path, monkeypatch):
    monkeypatch.setattr("app.reports.REPORTS_DIR", tmp_path)
    report = OperationReport(operation="organization")
    report.add_file_operation("/a/file.jpg", "/a/Images/file.jpg", "MOVED")
    report.add_file_operation("/a/x.xyz", "", "SKIPPED", "Unsupported extension")
    report.finish()
    path = save_csv_report(report)
    assert path.exists()
    lines = path.read_text().splitlines()
    assert lines[0] == "original_path,destination_path,status,error"
    assert "MOVED" in lines[1]
    assert "SKIPPED" in lines[2]


def test_load_latest_report_no_reports(tmp_path, monkeypatch):
    monkeypatch.setattr("app.reports.REPORTS_DIR", tmp_path)
    result = load_latest_report()
    assert result is None


def test_load_latest_report_returns_most_recent(tmp_path, monkeypatch):
    monkeypatch.setattr("app.reports.REPORTS_DIR", tmp_path)
    report = OperationReport(operation="scan", files_scanned=99)
    report.finish()
    save_json_report(report)
    data = load_latest_report()
    assert data["files_scanned"] == 99
