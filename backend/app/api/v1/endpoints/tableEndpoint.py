from fastapi import APIRouter

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("/")
async def getTables():
    pass


@router.get("/{tableName}/records")
async def getRecords(tableName: str):
    pass


@router.post("/{tableName}/records")
async def createRecord(tableName: str):
    pass


@router.put("/{tableName}/records/{recordId}")
async def updateRecord(tableName: str, recordId: int):
    pass


@router.delete("/{tableName}/records/{recordId}")
async def deleteRecord(tableName: str, recordId: int):
    pass
