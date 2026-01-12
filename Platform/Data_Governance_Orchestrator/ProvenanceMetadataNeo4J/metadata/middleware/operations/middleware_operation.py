import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from ... import const as c
from ...dbmanager.neo4j_connection import Neo4JConnection
from ...token import get_token


class MiddlewareOperation(ABC):
    """
    abstract base class for middleware-operations
    """
    pattern: re.Pattern
    db: Neo4JConnection

    def __init__(self, regex: str, db: Neo4JConnection):
        """
        constructor
        :param regex: regex for method@path
        :param db: dbmanager object
        """
        self.pattern = re.compile(regex)
        self.db = db

    @abstractmethod
    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        """
        code to be executed, when the operation gets called
        :param operation: method@path string
        :param user_responsible: user responsible for the operation
        :param response_json: JSON of the response body
        :returns: None
        """
        pass

    def get_pattern(self) -> re.Pattern:
        """
        gets pattern-object for operation
        :returns: pattern-object for operation
        """
        return self.pattern

    async def get_governance_id(self, id: str, kind: str) -> str | None:
        """
        return the governance id for the given id
        :param: id: id to be resolved
        :param kind: kind of object
        :returns: governance id for the given id or None in case of error
        """
        token: str | None = await get_token()
        if not token:
            return None
        if kind == 'strategy':
            kind = 'strategie'
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f'{c.REST_URL}/{kind}s/{id}',
                                       headers={'Authorization': token})
                return res.json()['_governance_id']
        except Exception:
            return None
