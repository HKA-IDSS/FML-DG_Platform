from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class UploadTrainedModelOperation(MiddlewareOperation):
    """
    UploadTrainedModelOperation
    """
    regex: str = '(POST@/results/models/)(.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for UploadTrainedModelOperation
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
            configuration_id = res.group(2)  # pyright: ignore
            filename = response_json.get('filename', 'unknown')
            
            self.db.track_trained_model_upload(
                configuration_id=configuration_id,
                filename=filename,
                user_id=user_responsible
            )
        except (KeyError, AttributeError):
            pass