from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.agent_model import AgentModel
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/groups', tags=['groups'])


@router.get('', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all groups as a JSON.'
                }
})
async def get_all_groups() -> list[EntityModel]:
    """
    returns all groups
    :return: JSON-response of all groups
    """
    return [EntityModel(**group) for group in db.get_all_groups()]


@router.get('/{group_id}/members', response_model=list[AgentModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns users in group as JSON.'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Group does not exist.'
                }
})
async def get_users_in_group(group_id: str) -> list[AgentModel]:
    """
    returns all users in a group
    :param group_id: id of the group
    :return: JSON-response of all members of a group
    """
    return [AgentModel(**agent) for agent in db.get_members_of_group(group_id)]
