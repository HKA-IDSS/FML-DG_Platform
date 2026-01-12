from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UpdateOrganisationOperation(MiddlewareOperation):
    """
    UpdateOrganisationOperation
    """
    regex: str = '(PUT@/organisations/)(.+)'

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
            self.db.create_organisation(response_json['_governance_id'])
        except KeyError:
            # There was an error while updating the organisation.
            # There is nothing to be done here
            pass
