"""
Unit test cho tool listTables (trả danh sách tên bảng từ SQLite).

Kiểm tra:
  - listTables() trả về đúng tên các bảng nghiệp vụ.
  - Loại trừ bảng nội bộ của SQLite (sqlite_sequence, sqlite_stat...).
  - Kết quả được sắp xếp theo tên.
"""

import os
import sqlite3

import pytest

from app.agent.tools import listTables
from app.core.config import settings


@pytest.fixture
def tempDb(tmp_path, monkeypatch):
    """Tạo SQLite tạm có AUTOINCREMENT (sinh sqlite_sequence) rồi trỏ config vào đó."""
    dbPath = tmp_path / "test.db"
    conn = sqlite3.connect(dbPath)
    # AUTOINCREMENT khiến SQLite tự tạo bảng nội bộ sqlite_sequence.
    conn.execute("CREATE TABLE Employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    conn.execute("CREATE TABLE Departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    conn.execute("INSERT INTO Employees (name) VALUES ('An')")
    conn.commit()
    conn.close()

    monkeypatch.setattr(settings, "database_path", str(dbPath))
    return dbPath


def test_list_tables_returns_business_table_names(tempDb):
    """Trả về đúng tên các bảng nghiệp vụ, sắp xếp theo tên."""
    assert listTables() == ["Departments", "Employees"]


def test_list_tables_excludes_sqlite_internals(tempDb):
    """Bảng nội bộ sqlite_sequence (do AUTOINCREMENT) phải bị loại trừ."""
    tables = listTables()
    assert "sqlite_sequence" in _rawTableNames(tempDb), "fixture phải sinh sqlite_sequence"
    assert not any(name.startswith("sqlite_") for name in tables)


@pytest.mark.skipif(
    not os.path.exists("data/datapilot.db"),
    reason="cần data/datapilot.db (chạy: python data/seed.py)",
)
def test_list_tables_returns_eight_hr_tables(monkeypatch):
    """Trên DB HR đã seed, listTables trả đúng 8 bảng nghiệp vụ."""
    monkeypatch.setattr(settings, "database_path", "data/datapilot.db")
    expected = [
        "Attendance",
        "BaseSalary",
        "ChatHistory",
        "Departments",
        "EmployeeProfiles",
        "Employees",
        "LeaveRequests",
        "SalaryHistory",
    ]
    assert listTables() == expected


def _rawTableNames(dbPath) -> list[str]:
    conn = sqlite3.connect(dbPath)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return [r[0] for r in rows]
