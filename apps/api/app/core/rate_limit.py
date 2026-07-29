"""SlowAPI-based rate limiting middleware.

Usage:
    @router.get('/endpoint')
    @limiter.limit("100/minute")
    async def endpoint(request: Request, ...):
        ...

To enable per-route, install: pip install slowapi
Then add:

    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.middleware import SlowAPIMiddleware

    limiter = Limiter(key_func=get_remote_address)

    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith('/api/v1'):
            client_ip = request.client.host if request.client else 'unknown'
            now = time.time()
            window = now - 60

            self.clients[client_ip] = [t for t in self.clients[client_ip] if t > window]

            if len(self.clients[client_ip]) >= self.requests_per_minute:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={'detail': 'Rate limit exceeded. Try again in 60 seconds.'},
                    headers={'Retry-After': '60'},
                )

            self.clients[client_ip].append(now)

        return await call_next(request)
