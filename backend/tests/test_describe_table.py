"""
Unit test cho tool describeTable (mô tả schema của một bảng từ SQLite).

Kiểm tra:
  - Bảng hợp lệ -> list cột, mỗi cột có 'name' và 'type'.
  - Bảng không tồn tại -> trả {"error": ...} (không phải list rỗng im lặng).
  - Tên bảng gây injection/lỗi cú pháp -> trả {"error": ...} (không raise).
"""

import os
import sqlite3

import pytest

from app.agent.tools import describeTable
from app.core.config import settings


@pytest.fixture
def tempDb(tmp_path, monkeypatch):
    """Tạo SQLite tạm với một bảng nghiệp vụ rồi trỏ config vào đó."""
    dbPath = tmp_path / "test.db"
    conn = sqlite3.connect(dbPath)
    conn.execute(
        "CREATE TABLE Employees ("
        "EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "HoTen TEXT NOT NULL, "
        "NgayVaoLam DATE)"
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(settings, "database_path", str(dbPath))
    return dbPath


def test_describe_table_returns_columns_with_name_and_type(tempDb):
    """Trả về list cột, mỗi cột tối thiểu có khóa 'name' và 'type'."""
    columns = describeTable("Employees")
    assert isinstance(columns, list)
    names = [c["name"] for c in columns]
    assert names == ["EmployeeID", "HoTen", "NgayVaoLam"]
    assert all("name" in c and "type" in c for c in columns)
    pk = next(c for c in columns if c["name"] == "EmployeeID")
    assert pk["pk"] == 1


def test_describe_table_unknown_returns_error(tempDb):
    """Bảng không tồn tại -> {"error": ...}, không phải list rỗng."""
    result = describeTable("KhongTonTai")
    assert isinstance(result, dict) and "error" in result


def test_describe_table_rejects_injection_name(tempDb):
    """Tên bảng gây lỗi cú pháp PRAGMA -> trả error, không raise."""
    result = describeTable("Employees]")
    assert isinstance(result, dict) and "error" in result


def test_describe_table_empty_name_returns_error(tempDb):
    """Tên rỗng -> {"error": ...}."""
    result = describeTable("")
    assert isinstance(result, dict) and "error" in result


@pytest.mark.skipif(
    not os.path.exists("data/datapilot.db"),
    reason="cần data/datapilot.db (chạy: python data/seed.py)",
)
def test_describe_table_real_employees(monkeypatch):
    """Trên DB HR đã seed, bảng Employees có cột khóa chính EmployeeID."""
    monkeypatch.setattr(settings, "database_path", "data/datapilot.db")
    columns = describeTable("Employees")
    assert isinstance(columns, list) and len(columns) > 0
    byName = {c["name"]: c for c in columns}
    assert "EmployeeID" in byName
    assert byName["EmployeeID"]["pk"] == 1
