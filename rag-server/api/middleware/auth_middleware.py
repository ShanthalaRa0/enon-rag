from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        api_key = request.headers.get("x-api-key")

        if not api_key:

            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing API Key"
                }
            )

        response = await call_next(request)

        return response