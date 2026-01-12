from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UpdateUserOperation(MiddlewareOperation):
    """
    UpdateUserOperation
    """
    regex: str = '(PUT@/users/)(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for UpdateUserOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        try:
            self.db.create_user(response_json['_governance_id'],
                                response_json['organisation_id'],
                                user_responsible)
        except KeyError:
            # There was an error while updating the user.
            # There is nothing to be done here
            pass
