from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UpdateQROperation(MiddlewareOperation):
    """
    UpdateQROperation
    """
    regex: str = '(PUT@/strategies/)(.+)/quality_requirements/(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for UpdateQROperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        # ask if something should happen
        pass
