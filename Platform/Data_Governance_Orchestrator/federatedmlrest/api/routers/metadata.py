import yaml

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from starlette import status

import httpx

from federatedmlrest.api.models.metadata_models import (
    ActivityModel,
    NumOfActionModel,
    GroupedActivityModel,
    EntityModel,
    AgentModel
)

with open('federatedmlrest/config.yml', 'r') as file:
    config = yaml.safe_load(file)

API_HOST: str = config['metadata']['host']
API_PORT: str = config['metadata']['port']


router: APIRouter = APIRouter(prefix='/metadata', tags=['metadata'])


@router.get('/actions', response_model=list[ActivityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns actions taken. If a start_time is '
                                   'given the response will contain all '
                                   'actions taken since the start_time. If an '
                                   'end_time is given the response will '
                                   'contain all actions taken before the '
                                   'end_time. If both a start_time and '
                                   'end_time are given the response will '
                                   'contain all actions taken in that '
                                   'interval. If neither a start_time or '
                                   'end_time is given the response will '
                                   'contain all actions taken by the user.'
                }
            })
async def get_actions(start_time: datetime | None = Query(default=None),
                      end_time: datetime | None = Query(default=None)
                      ) -> list[ActivityModel]:
    """
    returns all actions
    If a start_time is given then it will return all actions taken since
    If an end_time is given it will return all actions taken until
    If both a start and end_time are given all actions in that interval will
    be returned
    :param start_time: start_time of interval
    :param end_time: end_time of interval
    :returns: JSON-response of all actions
    """
    url: str = f'http://{API_HOST}:{API_PORT}/actions'
    if start_time and not end_time:
        url += f'?start_time={start_time}'
    elif end_time and not start_time:
        url += f'?end_time={end_time}'
    elif start_time and end_time:
        url += f'?start_time={start_time}&end_time={end_time}'

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [ActivityModel(**a) for a in res.json()]


@router.get('/actions/num', response_model=list[NumOfActionModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns a map of user and number of '
                                   'actions during the given interval'
                }
})
async def get_num_of_actions(start_time: datetime | None = Query(default=None),
                             end_time: datetime | None = Query(default=None)
                             ) -> list[NumOfActionModel]:
    """
    returns a map of user and number of actions taken within the given interval
    :param start_time: start of interval
    :param end_time: end of interval
    :returns:  JSONResponse containing a map of user and number of actions
    """
    url: str = f'http://{API_HOST}:{API_PORT}/actions/num'
    if start_time and not end_time:
        url += f'?start_time={start_time}'
    elif end_time and not start_time:
        url += f'?end_time={end_time}'
    elif start_time and end_time:
        url += f'?start_time={start_time}&end_time={end_time}'

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [NumOfActionModel(**a) for a in res.json()]


@router.get('/actions/more', response_model=list[NumOfActionModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns a map of user and number of '
                                   'actions during the given interval for all '
                                   'users that have taken more than num '
                                   'actions'
                }
})
async def get_more_than_num_actions(num: int,
                                    start_time: datetime | None = Query(
                                        default=None),
                                    end_time: datetime | None = Query(
                                        default=None)
                                    ) -> list[NumOfActionModel]:
    """
    returns a map of user and number of actions taken within the given
    interval for all user that have taken more than num actions
    :param start_time: start of interval
    :param end_time: end of interval
    :returns: a JSONRespone containing a map of user and number of actions
              taken within the given interval for all user that have taken
              more than num actions
    """
    url: str = f'http://{API_HOST}:{API_PORT}/actions/more?num={num}'
    if start_time and not end_time:
        url += f'&start_time={start_time}'
    elif end_time and not start_time:
        url += f'&end_time={end_time}'
    elif start_time and end_time:
        url += f'&start_time={start_time}&end_time={end_time}'

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [NumOfActionModel(**a) for a in res.json()]


@router.get('/actions/related_to/{gov_id}',
            response_model=list[GroupedActivityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all actions related to the object'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Object does not exist.'
                }
            })
async def get_actions_for_object(gov_id: str) -> list[GroupedActivityModel]:
    """
    Returns all actions related to the object
    :param start_time: start of interval
    :param end_time: end of interval
    :returns: a JSONRespone containing all actions related to the object
    """
    url: str = f'http://{API_HOST}:{API_PORT}/actions/related_to/{gov_id}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        if res.status_code != httpx.codes.OK:
            raise HTTPException(404, 'Object does not exist')
        return [GroupedActivityModel(**a) for a in res.json()]


@router.get('/actions/grouped_by_user',
            response_model=list[GroupedActivityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Same as /actions but groups result by user'
                }
            })
async def get_actions_group(start_time: datetime | None = Query(default=None),
                            end_time: datetime | None = Query(default=None)
                            ) -> list[GroupedActivityModel]:
    """
    returns all actions
    If a start_time is given then it will return all actions taken since
    If an end_time is given it will return all actions taken until
    If both a start and end_time are given all actions in that interval will
    be returned
    :param start_time: start_time of interval
    :param end_time: end_time of interval
    :returns: JSON-response of all actions
    """
    url: str = f'http://{API_HOST}:{API_PORT}/actions/grouped_by_user'
    if start_time and not end_time:
        url += f'?start_time={start_time}'
    elif end_time and not start_time:
        url += f'?end_time={end_time}'
    elif start_time and end_time:
        url += f'?start_time={start_time}&end_time={end_time}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [GroupedActivityModel(**a) for a in res.json()]


@router.get('/configurations',
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
    url: str = f'http://{API_HOST}:{API_PORT}/configurations'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**c) for c in res.json()]


@router.get('/dataset', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Return all datasets as a JSON.'
                }
})
async def get_all_datasets() -> list[EntityModel]:
    """
    returns all datasets
    :return: JSON-response of all datasets
    """
    url: str = f'http://{API_HOST}:{API_PORT}/datasets'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**d) for d in res.json()]


@router.get('/groups', response_model=list[EntityModel],
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
    url: str = f'http://{API_HOST}:{API_PORT}/groups'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**g) for g in res.json()]


@router.get('/groups/{group_id}/members', response_model=list[AgentModel],
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
    url: str = f'http://{API_HOST}:{API_PORT}/groups/{group_id}/members'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        if res.status_code != httpx.codes.OK:
            raise HTTPException(404, 'Group does not exist')
        return [AgentModel(**a) for a in res.json()]


@router.get('/ml-models', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all ml-models as a JSON.'
                }
})
async def get_all_models() -> list[EntityModel]:
    """
    returns all ml-models
    :return: JSON-response of all ml-models
    """
    url: str = f'http://{API_HOST}:{API_PORT}/ml-models'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**g) for g in res.json()]


@router.get('/organisations', response_model=list[AgentModel],
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
    url: str = f'http://{API_HOST}:{API_PORT}/organisations'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [AgentModel(**a) for a in res.json()]


@router.get('/proposals', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Return all proposals as a JSON.'
                }
})
async def get_all_proposals() -> list[EntityModel]:
    url: str = f'http://{API_HOST}:{API_PORT}/proposals'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**p) for p in res.json()]


@router.get('/strategies', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all strategies as a JSON.'
                }
})
async def get_all_strategies() -> list[EntityModel]:
    """
    Returns all strategies
    """
    url: str = f'http://{API_HOST}:{API_PORT}/strategies'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**s) for s in res.json()]


@router.get('/strategies/{id}/qr', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all quality requirements for the '
                                   'given strategy as a JSON.'
                }
})
async def get_qr(id: str) -> list[EntityModel]:
    """
    Returns all strategies
    """
    url: str = f'http://{API_HOST}:{API_PORT}/strategies/{id}/qr'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [EntityModel(**qr) for qr in res.json()]


@router.get('/users', response_model=list[AgentModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns a list of all users.'
                }
})
async def get_all_users() -> list[AgentModel]:
    """
    Returns a list of all users
    """
    url: str = f'http://{API_HOST}:{API_PORT}/users'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        return [AgentModel(**a) for a in res.json()]


@router.get('/users/{gov_id}', response_model=AgentModel,
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
    url: str = f'http://{API_HOST}:{API_PORT}/users/{gov_id}'
    if version:
        url += f'?version={version}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        if res.status_code != httpx.codes.OK:
            raise HTTPException(404, 'User or version of user does not exist')
        return AgentModel(**res.json())


@router.get('/users/{gov_id}/actions', response_model=GroupedActivityModel,
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
    url: str = f'http://{API_HOST}:{API_PORT}/users/{gov_id}/actions'
    if start_time and not end_time:
        url += f'?start_time={start_time}'
    elif end_time and not start_time:
        url += f'?end_time={end_time}'
    elif start_time and end_time:
        url += f'?start_time={start_time}&end_time={end_time}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        if res.status_code != httpx.codes.OK:
            raise HTTPException(404, 'The requested user does not exist or '
                                     'has taken no action')
        return GroupedActivityModel(**res.json())


@router.get('/users/{relationship}/to/{gov_id}',
            response_model=list[AgentModel],
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
    url: str = f'http://{API_HOST}:{API_PORT}/users/{relationship}/to/{gov_id}'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        if res.status_code != httpx.codes.OK:
            raise HTTPException(404, 'The requested object does not exist')
        return [AgentModel(**a) for a in res.json()]
