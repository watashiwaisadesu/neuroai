from fastapi import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time


def register_middleware(app: FastAPI) -> FastAPI:

    @app.middleware("http")
    async def middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["https://startling-sfogliatella-0d861c.netlify.app","http://79.142.54.154","https://neuroai.kz" ,"http://localhost:63342", "https://api.neuroai.kz", "http://localhost:8080","http://neuroai.kz:8001", "http://127.0.0.1:8000"],
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )












