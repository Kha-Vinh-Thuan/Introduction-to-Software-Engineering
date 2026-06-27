from fastapi import APIRouter
from app.api.controller.endpoints import chatEndpoint
from app.services.tableService import TableService
apiRouter = APIRouter(prefix="/api/v1")
apiRouter.include_router(chatEndpoint.router)

tableService = TableService()
@apiRouter.get("/tables")
def getTables():
    return tableService.getTables()

@apiRouter.get("/tables/{name}/records")
def getRecords(name: str, page: int = 1, pageSize: int = 50, search: str = ""):
    return tableService.getRecords(name, page, pageSize, search)

@apiRouter.get("/tables/{name}/sortedrecords/{column}")
def getSortedRecords(name: str, column: str, order: str = "ASC", page: int = 1, pageSize: int = 50):
    return tableService.getSortedRecords(name, column, order, page, pageSize)

@apiRouter.get("/tables/{name}/records/{id}")
def getRecordById(name: str, id: int):
    return tableService.getRecordById(name, id)

@apiRouter.post("/tables/{name}/records")
def createRecord(name: str):
    return tableService.createRecord(name)

@apiRouter.put("/tables/{name}/records/{id}")
def updateRecord(name: str, id: int, data: dict):
    return tableService.updateRecord(name,id,data)

@apiRouter.delete("/tables/{name}/records/{id}")
def deleteRecord(name: str, id: int):
    return tableService.deleteRecord(name,id)

@apiRouter.get("/schema/{name}")
def getTableSchema(name: str):
    return tableService.getTableSchema(name)

