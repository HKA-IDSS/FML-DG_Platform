from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class CreateGroupOperation(MiddlewareOperation):
    """
    Create Group Operation
    """
    regex: str = '(POST@/groups)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for Group Operation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        try:
            self.db.create_group(response_json['_governance_id'],
                                 user_responsible)
        except KeyError:
            # There was an error while creating the group.
            # There is nothing to be done here
            pass
