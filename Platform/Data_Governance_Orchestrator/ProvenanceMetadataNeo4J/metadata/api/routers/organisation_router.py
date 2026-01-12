from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.agent_model import AgentModel

router: APIRouter = APIRouter(prefix='/organisations', tags=['organisations'])


@router.get('', response_model=list[AgentModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all organisations as a JSON.'
                }
})
async def get_all_organisations() -> list[AgentModel]:
    """
    returns all organisations
    :return: JSON-response of all organisations
    """
    return [AgentModel(**org) for org in db.get_all_organisations()]
