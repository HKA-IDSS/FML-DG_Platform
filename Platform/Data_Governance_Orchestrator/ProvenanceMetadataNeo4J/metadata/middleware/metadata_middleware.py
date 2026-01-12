import json
import jwt

from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .. import const as c
from ..dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operations_manager import OperationManager


class MetadataMiddleware(BaseHTTPMiddleware):
    """
    middleware that manages the metadata-database
    """
    db: Neo4JConnection
    operation_manager: OperationManager

    def __init__(self, app):
        """
        constructor for middleware
        :param app:
        """
        super().__init__(app)
        self.db = Neo4JConnection(c.NEO4J_URL,
                                  authorization=c.NEO4J_AUTH,
                                  database=c.NEO4J_DATABASE)
        self.operation_manager = OperationManager(self.db)

    async def dispatch(self, request: Request, call_next):
        """
        dispatch for the middleware
        :param request: request to the api
        :param call_next: call api
        :return: response object
        """
        user_responsible: str = ''
        response_body: Any
        response_json: Any
        response: Response = await call_next(request)
        try:
            token: str = request.headers['Authorization']
            user_responsible: str = jwt.decode(
                token[7:], options={"verify_signature": False})['sub']
        except Exception:
            pass
        try:
            response_body = b""
            async for chunk in response.body_iterator:  # pyright: ignore
                response_body += chunk
        except Exception:
            response_body = None
        try:
            response_json = json.loads(response_body)
        except Exception:
            response_json = None
        await self.operation_manager.execute(
            f'{request.method}@{request.url.path}',
            user_responsible,
            response_json
        )
        if response_body:
            return Response(content=response_body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type)
        else:
            return response
