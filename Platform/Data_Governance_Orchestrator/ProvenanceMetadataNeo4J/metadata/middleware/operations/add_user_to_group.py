from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class AddUserToGroupOperation(MiddlewareOperation):
    """
    AddUserToGroup Operation
    """
    regex: str = '(POST@/groups/)(.+)(/add/)(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for AddUserToGroup Operation
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
            self.db.add_user_to_group(res.group(2),  # pyright: ignore
                                      user_responsible,
                                      res.group(4))  # pyright: ignore
