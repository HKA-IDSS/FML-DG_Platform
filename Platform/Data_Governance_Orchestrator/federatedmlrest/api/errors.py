"""All errors strings."""

BAD_REQUEST = "The request is not supported."
MLMODEL_IN_USE = "The ML Model is currently in use and thus cannot be deleted."
DATASET_IN_USE = "The Dataset is currently in use and thus cannot be deleted."
GENERIC_NOT_FOUND = "A specified resource was not found."
GROUP_NOT_FOUND = "The specified group does not exist."
MEMBER_NOT_FOUND = "The specified user was not found in the group."
STRATEGY_NOT_FOUND = "The specified strategy was not found in the group."
CONFIGURATION_NOT_FOUND = "The specified configuration was not found in the strategy."
DATASET_NOT_FOUND = "The specified dataset does not exist."
MLMODEL_NOT_FOUND = "The specified ml model does not exist."
HYPERPARAMETER_NOT_FOUND = "The specified hyperparameter does not exist."
MEMBER_NOT_IN_GROUP = "Member is not in the group, therefore unauthorized."
PROPOSAL_NOT_FOUND = "The specified Proposal does not exist."
NOT_PROPOSABLE = "The specified Object is not proposable."
QUALITY_REQUIREMENT_NOT_FOUND = "Quality Requirement does not exist."
INCORRECT_USER = "Incorrect username or password"
VOTE_PRIORITY_ALREADY_EXISTS = (
    "Vote with the same priority already exists in another proposal."
)
USER_NOT_FOUND = "The specified user was not found."
ORGANISATION_NOT_FOUND = "The specified organisation was not found."
FILE_NOT_EXISTS = "The evaluation results do not exist."
KEYCLOAK_CREATE_USER = "Keycloak user could not be created."
KEYCLOAK_DELETE_USER = "Keycloak user could not be deleted."
USER_ALREADY_IN_GROUP = "The user is already in the group"
MODEL_TYPE_NOT_FOUND = "The model type provided is not valid. It must be one of the following: mlp, xgboost, custom."
EXISTING_QUALITY_REQUIREMENT = ("There cannot be two quality requirements of correctness for the same metric."
                                "Please, propose an update for the existing one.")

TRAINING_CONFIGURATION_RESULTS_NOT_FOUND = ("There is no information about this training. If a training configuration"
                                            "accepted exists, it means this training has not finished yet.")