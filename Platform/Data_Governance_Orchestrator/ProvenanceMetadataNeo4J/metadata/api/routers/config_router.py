from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/configurations',
                              tags=['configurations'])


@router.get('',
            response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns configurations as a JSON.'
                }
            })
async def get_all_configurations() -> list[EntityModel]:
    """
    Returns all configurations for the given strategy
    """
    return [
        EntityModel(**config) for config in
        db.get_configurations()
    ]


@router.get('/{config_id}/root-cause',
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns the root cause analysis for the configuration, '
                                  'tracing back everything that led to its creation.'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Configuration does not exist.'
                }
            })
async def get_configuration_root_cause(config_id: str) -> dict:
    """
    Get root cause analysis for a configuration.
    
    This endpoint traces back everything that led to the creation of a configuration,
    including:
    - The proposal that became the configuration
    - Votes on the proposal
    - Users who voted
    - ML model and dataset linked
    - Strategy and group associations
    - All related activities and entities
    
    Uses graph traversal to follow provenance relationships in the graph.
    """
    return await db.get_configuration_root_cause(config_id)
