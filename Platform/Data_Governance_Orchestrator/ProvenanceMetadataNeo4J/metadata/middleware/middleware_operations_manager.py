from typing import Any

from ..dbmanager.neo4j_connection import Neo4JConnection
from .operations.add_config import AddConfigOperation
from .operations.add_qualitiy_requirement import AddQualityRequirementOperation
from .operations.add_user_to_group import AddUserToGroupOperation
from .operations.create_dataset import CreateDatasetOperation
from .operations.create_group import CreateGroupOperation
from .operations.create_ml_model import CreateMLModelOperation
from .operations.create_organisation import CreateOrganisationOperation
from .operations.create_proposal import CreateProposalOperation
from .operations.create_configuration_proposal import CreateConfigurationProposalOperation
from .operations.create_quality_requirement_proposal import CreateQualityRequirementProposalOperation
from .operations.create_strategy import CreateStrategyOperation
from .operations.create_user import CreateUserOperation
from .operations.delete_config import DeleteConfigOperation
from .operations.delete_dataset import DeleteDatasetOperation
from .operations.delete_group import DeleteGroupOperation
from .operations.delete_ml_model import DeleteMLModelOperation
from .operations.delete_organisation import DeleteOrganisationOperation
from .operations.delete_proposal import DeleteProposalOperation
from .operations.delete_strategy import DeleteStrategyOperation
from .operations.delete_user import DeleteUserOperation
from .operations.delete_vote import DeleteVoteOperation
from .operations.delete_qr import DeleteQROperation
from .operations.end_voting import EndVotingOperation
from .operations.middleware_operation import MiddlewareOperation
from .operations.update_config import UpdateConfigOperation
from .operations.update_dataset import UpdateDatasetOperation
from .operations.update_group import UpdateGroupOperation
from .operations.update_model import UpdateModelOperation
from .operations.update_organisation import UpdateOrganisationOperation
from .operations.update_qr import UpdateQROperation
from .operations.update_strategy import UpdateStrategyOperation
from .operations.update_user import UpdateUserOperation
from .operations.upload_evaluation_results import UploadEvaluationResultsOperation
from .operations.upload_trained_model import UploadTrainedModelOperation
from .operations.vote import VoteOperation


class OperationManager:
    """
    Class that manages the operations for the metadata-middleware
    """
    operations: list[MiddlewareOperation]

    def __init__(self, db: Neo4JConnection):
        """
        Constructor for OperationManager
        """
        self.operations = [
            AddConfigOperation(db),
            AddQualityRequirementOperation(db),
            AddUserToGroupOperation(db),
            CreateDatasetOperation(db),
            CreateGroupOperation(db),
            CreateMLModelOperation(db),
            CreateOrganisationOperation(db),
            CreateProposalOperation(db),
            CreateConfigurationProposalOperation(db),
            CreateQualityRequirementProposalOperation(db),
            CreateStrategyOperation(db),
            CreateUserOperation(db),
            DeleteConfigOperation(db),
            DeleteStrategyOperation(db),
            DeleteUserOperation(db),
            DeleteGroupOperation(db),
            DeleteMLModelOperation(db),
            DeleteDatasetOperation(db),
            DeleteOrganisationOperation(db),
            DeleteProposalOperation(db),
            DeleteQROperation(db),
            DeleteVoteOperation(db),
            EndVotingOperation(db),
            UpdateConfigOperation(db),
            UpdateDatasetOperation(db),
            UpdateGroupOperation(db),
            UpdateModelOperation(db),
            UpdateOrganisationOperation(db),
            UpdateQROperation(db),
            UpdateStrategyOperation(db),
            UpdateUserOperation(db),
            UploadEvaluationResultsOperation(db),
            UploadTrainedModelOperation(db),
            VoteOperation(db)
        ]

    def get_operation(self, operation: str) -> MiddlewareOperation | None:
        """
        retrieves operation matching the given method@path
        :param operation: operation in the form method@path
        :returns: the found operation or None
        """
        for op in self.operations:
            if op.get_pattern().fullmatch(operation):
                return op
        return None

    async def execute(self,
                      operation: str,
                      user_responsible: str,
                      response_json: Any
                      ) -> None:
        """
        executes the operation
        :param user_responsible: id of the user responsible for the operation.
        :param operation: operation in the form method@path
        :param response_json: response body in JSON format
        :returns: None
        """
        op: MiddlewareOperation | None = self.get_operation(operation)
        if op:
            await op.execute(operation, user_responsible, response_json)
