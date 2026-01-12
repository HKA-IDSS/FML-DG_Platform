from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class VoteOperation(MiddlewareOperation):
    """
    VoteOperation
    """
    regex: str = '(POST@/proposals/)(.+)(/votes)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for VoteOperation
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
            vote: str
            index: int = len(response_json['votes']) - 1
            try:
                vote = response_json['votes'][index]['decision']
            except KeyError:
                vote = response_json['votes'][index]['priority']
            self.db.vote(res.group(2),  # pyright: ignore
                         vote,
                         user_responsible)
        except KeyError:
            # Error while voting
            # Nothing to be done here
            pass
