from fastapi import APIRouter

router = APIRouter(prefix="/import-export", tags=["Import/Export"])


@router.post("/import/{tableName}")
async def importCsv(tableName: str):
    pass


@router.get("/export/{tableName}")
async def exportCsv(tableName: str):
    pass
