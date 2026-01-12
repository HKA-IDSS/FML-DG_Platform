import json

from datetime import datetime

from fastapi import APIRouter, Query
from starlette import status

from ..database_connection import db_connection as db
from ..models.activity_model import ActivityModel
from ..models.grouped_activity_model import GroupedActivityModel
from ..models.agent_model import AgentModel
from ...dbmanager.exceptions.no_actions import NoActionException

router: APIRouter = APIRouter(prefix='/users', tags=['users'])


@router.get('', response_model=list[AgentModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns a list of all users.'
                }
})
async def get_all_users() -> list[AgentModel]:
    """
    Returns a list of all users
    """
    return [AgentModel(**agent) for agent in db.get_all_users()]


@router.get('/{gov_id}', response_model=AgentModel,
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns a user as a JSON.'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'The requested user or version of the user '
                    'does not exist.'
                }
            })
async def get_user(gov_id: str, version: int | None = None) -> AgentModel:
    """
    Returns a users
    """
    return AgentModel(**db.get_user(gov_id, version)[0])


@router.get('/{gov_id}/actions', response_model=GroupedActivityModel,
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns actions taken by a user. If a '
                                   'start_time is given the response will '
                                   'contain all actions taken since the '
                                   'start_time. If an end_time is given the '
                                   'response will contain all actions taken '
                                   'before the end_time. If both a start_time '
                                   'and end_time are given the response will '
                                   'contain all actions taken in that interval'
                                   '. If neither a start_time or end_time is '
                                   'given the response will contain all '
                                   'actions taken by the user.'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'The requested user does not exist or has '
                                   'taken no action'
                }
            })
async def get_actions_by_user(gov_id: str,
                              start_time: datetime | None = Query(
                                  default=None),
                              end_time: datetime | None = Query(default=None)
                              ) -> GroupedActivityModel:
    """
    returns all actions by a user
    If a start_time is given then it will return all actions taken since
    If an end_time is given it will return all actions taken until
    If both a start and end_time are given all actions in that interval will
    be returned
    :param start_time: start_time of interval
    :param end_time: end_time of interval
    :param gov_id: id of the user
    :returns: JSON-response of all actions taken by a user
    """
    data = json.loads(
                json.dumps(
                    await db.get_actions(gov_id, start_time, end_time)
                    )
                )
    actions: list[dict] = list()

    for d in data:
        actions.append(
            {
                "name": d['name'],
                "affected_objects": d["affected_objects"],
                "start_time": d["start_time"],
                "end_time": d["end_time"]
            })

    try:
        out: dict = {
            "responsible": data[0]['responsible'],
            "actions": actions
        }
    except IndexError:
        raise NoActionException()
    return GroupedActivityModel(**out)


@router.get('/{relationship}/to/{gov_id}', response_model=list[AgentModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'returns all agents associated with the '
                                   'given object via the given relationship'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'The requested object does not exist.'
                }
})
async def get_agent_by_relationship(relationship: str,
                                    gov_id: str
                                    ) -> list[AgentModel]:
    """
    returns all agents associated with the given object via the given
    relationship
    :param relationship: end_time of interval
    :param gov_id: id of the object
    :returns: JSON-response of the agent
    """
    return [
        AgentModel(**agent) for agent in
        db.get_nodes_by_relationship(gov_id, relationship)
    ]
