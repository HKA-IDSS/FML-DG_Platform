from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class CreateUserOperation(MiddlewareOperation):
    """
    Create User Operation
    """
    regex: str = '(POST@/users)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for User Operation
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
            # user creation failed in kc, there is nothing to do here
            pass
