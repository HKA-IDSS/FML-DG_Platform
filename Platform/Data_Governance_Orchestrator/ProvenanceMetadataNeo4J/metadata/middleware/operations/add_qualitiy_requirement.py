from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class AddQualityRequirementOperation(MiddlewareOperation):
    """
    AddQualityRequirement
    """
    regex: str = '(POST@/strategies/)(.+)(/quality_requirements)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for AddQualityRequirement Operation
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
            self.db.add_quality_requirement(response_json['_id'],
                                            res.group(2),  # pyright: ignore
                                            user_responsible)
        except KeyError:
            # There was an error while creating the QualityRequirement.
            # There is nothing to be done here
            pass
