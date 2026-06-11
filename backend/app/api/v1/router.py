from fastapi import APIRouter
from app.api.v1.endpoints import (
    tableEndpoint,
    schemaEndpoint,
    chatEndpoint,
    reportEndpoint,
    importExportEndpoint,
)

apiRouter = APIRouter(prefix="/api/v1")

apiRouter.include_router(tableEndpoint.router)
apiRouter.include_router(schemaEndpoint.router)
apiRouter.include_router(chatEndpoint.router)
apiRouter.include_router(reportEndpoint.router)
apiRouter.include_router(importExportEndpoint.router)
