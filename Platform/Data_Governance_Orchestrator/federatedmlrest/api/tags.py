from enum import Enum


class Tags(Enum):
    """Route Tags."""

    GROUPS: str = 'Groups'
    MEMBERS: str = 'Members'
    STRATEGIES: str = 'Strategies'
    CONFIGURATIONS: str = 'Configurations'
    ML_MODELS: str = 'ML Models'
    DATASETS: str = 'Datasets'
    HYPERPARAMETER: str = 'Hyperparameter'
    PROPOSALS: str = 'Proposals'
    QUALITY_REQUIREMENTS: str = 'Quality Requirements'
    USERS: str = 'Users'
    ORGANISATIONS: str = 'Organisations'
    RESULTS = 'Results'
