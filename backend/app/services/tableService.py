from app.repositories.tableRepository import TableRepository


class TableService:
    def __init__(self):
        self.tableRepository = TableRepository()

    def getTables(self):
        return self.tableRepository.findAllTables()

    def getTableSchema(self, tableName: str):
        return self.tableRepository.findTableSchema(tableName)

    def getRecords(self, tableName: str, page: int = 1, pageSize: int = 50, search: str = ""):
        return self.tableRepository.findRecords(tableName, page, pageSize, search)
    
    def getSortedRecords(self, tableName: str, sortColumn: str, sortOrder: str = "ASC", page: int = 1, pageSize: int = 50):
        return self.tableRepository.getSortedRecords(tableName, sortColumn, sortOrder, page, pageSize)
    
    def getRecordById(self, tableName: str, recordId: int):
        return self.tableRepository.getRecordById(tableName, recordId)

    def createRecord(self, tableName: str, data: dict):
        return self.tableRepository.insertRecord(tableName, data)

    def updateRecord(self, tableName: str, recordId: int, data: dict):
        return self.tableRepository.updateRecord(tableName, recordId, data)

    def deleteRecord(self, tableName: str, recordId: int):
        return self.tableRepository.deleteRecord(tableName, recordId)
