from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UpdateConfigOperation(MiddlewareOperation):
    """
    UpdateConfigOperation
    """
    regex: str = ('(PUT@/groups/)(.+)(/strategies/)(.+)(/configurations/)(.+)'
                  '(/mlmodel|/dataset)')

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for UpdateConfigOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        try:
            res = search(self.regex, operation)
            self.db.update_config(res.group(7),  # pyright: ignore
                                  res.group(6),  # pyright: ignore
                                  response_json['ml_model_id'],
                                  response_json['dataset_id'],
                                  user_responsible)
        except KeyError:
            # There was an error while updating the config.
            # There is nothing to be done here
            pass
