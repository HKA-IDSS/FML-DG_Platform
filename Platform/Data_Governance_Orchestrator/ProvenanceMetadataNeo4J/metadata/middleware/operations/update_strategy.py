from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UpdateStrategyOperation(MiddlewareOperation):
    """
    UpdateStrategyOperation
    """
    regex: str = '(PUT@/strategies/)(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for UpdateStrategyOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        try:
            self.db.create_strategy(response_json['_governance_id'],
                                    response_json['belonging_group'],
                                    user_responsible)
        except KeyError:
            # There was an error while updating the strategy.
            # There is nothing to be done here
            pass
