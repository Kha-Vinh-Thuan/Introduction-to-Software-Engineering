from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnInfo:
    name: str
    type: str
    notNull: bool
    defaultValue: Optional[str]
    isPrimaryKey: bool


@dataclass
class TableInfo:
    name: str
    rowCount: int
    columns: list[ColumnInfo]
