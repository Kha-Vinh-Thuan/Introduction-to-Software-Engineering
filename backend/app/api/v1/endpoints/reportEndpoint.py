from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/weekly")
async def getWeeklyReport():
    pass


@router.get("/")
async def getReports():
    pass
