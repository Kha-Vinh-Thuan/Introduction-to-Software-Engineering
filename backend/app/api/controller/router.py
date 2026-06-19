from fastapi import APIRouter
from app.api.controller.endpoints import chatEndpoint

apiRouter = APIRouter(prefix="/api/v1")
apiRouter.include_router(chatEndpoint.router)
