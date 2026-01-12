from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class CreateConfigurationProposalOperation(MiddlewareOperation):
    """
    CreateConfigurationProposalOperation
    """
    regex: str = '(POST@/proposals/configurations)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for CreateConfigurationProposalOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        try:
            self.db.create_proposal(response_json['_id'],
                                    response_json['strategy_id'],
                                    user_responsible)
        except KeyError:
            # There was an error while creating the proposal.
            # There is nothing to be done here
            pass