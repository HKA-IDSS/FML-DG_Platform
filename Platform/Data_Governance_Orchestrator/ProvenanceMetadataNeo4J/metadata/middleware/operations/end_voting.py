from re import search
from typing import Any

from ...dbmanager.neo4j_connection import Neo4JConnection
from .middleware_operation import MiddlewareOperation


class EndVotingOperation(MiddlewareOperation):
    """
    EndVotingOperation
    """
    regex: str = 'POST@/proposals/.+/(count_votes_configuration_proposals|count_votes_qr/.+)'

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for EndVotingOperation
        :param db: neo4j database connection
        """
        super().__init__(self.regex, db)

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        if response_json:
            res = search(self.regex, operation)
            # Extract strategy_id from the path
            # Format: POST@/proposals/{strategy_id}/count_votes_*
            path_parts = operation.split('/')
            strategy_id = path_parts[2]  # After "POST@", "proposals", this is the strategy_id
            endpoint_type = res.group(1) if res else ''  # pyright: ignore

            proposal_id = None
            # Determine proposal type and extract proposal_id based on the endpoint
            if 'configuration' in endpoint_type:
                proposal_type = 'configuration'
                # For configuration proposals, get the proposal_id from the winner field
                if 'winner' in response_json and response_json['winner']:
                    proposal_id = response_json['winner']
            else:  # quality requirement
                proposal_type = 'quality_requirement'
                # For QR proposals, get the proposal_id from the proposal field
                proposal_id = response_json.get('proposal')
            
            if proposal_id:
                self.db.end_voting(strategy_id,
                                   proposal_id,
                                   proposal_type,
                                   user_responsible)
                
                # Track additional entity creation based on type
                if proposal_type == 'configuration':
                    if 'created_configuration_id' in response_json and response_json['created_configuration_id']:
                        created_config_id = response_json['created_configuration_id']
                        model_id = response_json.get('created_configuration_model_id')
                        dataset_id = response_json.get('created_configuration_dataset_id')
                        group_id = response_json.get('created_configuration_group_id')
                        
                        self.db.add_configuration(
                            created_config_id,
                            strategy_id,
                            group_id,
                            model_id,
                            dataset_id,
                            user_responsible
                        )
                
                elif proposal_type == 'quality_requirement':
                    if response_json.get('accepted') and 'created_quality_requirement_id' in response_json and response_json['created_quality_requirement_id']:
                        created_qr_id = response_json['created_quality_requirement_id']
                        
                        self.db.add_quality_requirement(
                            created_qr_id,
                            strategy_id,
                            user_responsible
                        )

# Complete end_voting:
#
# 1. metadata/middleware/operations/end_voting.py
# - regex is done
# - execute function calls end_voting from Neo4jConnerction
#     - may need to change the arguments of the functions if additional
#       parameters are required
#     - double check that the given arguments are correct i.e. read the correct
#       field from the response body
#
# 2. metadata/dbmanager/neo4j_connection.py
# - end_voting function has been created
#     - may need to change the arguments given to the execute_query function
#
# 3. metadata/dbmanager/queries/interactions.py
# - END_VOTING query has been created but is incomplete and must be finished
#
# 4. metadata/middleware/middleware_operations_manager.py
# - uncomment line 68
