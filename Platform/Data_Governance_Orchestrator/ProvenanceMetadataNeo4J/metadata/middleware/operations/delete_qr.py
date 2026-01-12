from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class DeleteQROperation(MiddlewareOperation):
    """
    DeleteQROperation
    """
    regex: str = '(DELETE@/strategies/)(.+)(/quality_requirements/)(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for DeleteQROperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        if response_json:
            res = search(self.regex, operation)
            self.db.delete_entry(res.group(4),  # pyright: ignore
                                 user_responsible,
                                 'quality_requirement')
