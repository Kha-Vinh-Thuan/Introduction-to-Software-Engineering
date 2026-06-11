from pydantic import BaseModel
from typing import Any, Optional


class RecordCreateRequest(BaseModel):
    data: dict[str, Any]


class RecordUpdateRequest(BaseModel):
    data: dict[str, Any]


class RecordResponse(BaseModel):
    data: list[dict[str, Any]]
    total: int
    page: int
    pageSize: int


class TableListResponse(BaseModel):
    tables: list[dict]
