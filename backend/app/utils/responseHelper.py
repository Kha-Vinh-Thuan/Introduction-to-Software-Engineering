from fastapi.responses import JSONResponse


def successResponse(data, message: str = "Success", statusCode: int = 200):
    return JSONResponse(
        status_code=statusCode,
        content={"success": True, "message": message, "data": data},
    )


def errorResponse(message: str, statusCode: int = 400):
    return JSONResponse(
        status_code=statusCode,
        content={"success": False, "message": message, "data": None},
    )
