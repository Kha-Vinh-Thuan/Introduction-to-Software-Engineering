from fastapi import APIRouter

router = APIRouter(prefix="/schema", tags=["Schema"])


@router.get("/")
async def getSchema():
    pass


@router.get("/{tableName}")
async def getTableSchema(tableName: str):
    pass
