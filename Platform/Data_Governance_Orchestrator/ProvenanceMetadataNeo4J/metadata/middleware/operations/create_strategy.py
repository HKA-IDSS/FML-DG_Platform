from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class CreateStrategyOperation(MiddlewareOperation):
    """
    CreateStrategyOperation
    """
    regex: str = '(POST@/strategies)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for CreateStrategyOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        res = search(self.regex, operation)
        try:
            self.db.create_strategy(response_json['_governance_id'],
                                    response_json['belonging_group'],
                                    user_responsible)
        except KeyError:
            # There was an error while creating the strategy.
            # There is nothing to be done here
            pass
