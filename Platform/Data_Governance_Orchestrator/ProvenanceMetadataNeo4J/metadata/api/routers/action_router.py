import json

from datetime import datetime

from fastapi import APIRouter, Query
from starlette import status

from ..database_connection import db_connection as db
from ..models.activity_model import ActivityModel
from ..models.grouped_activity_model import GroupedActivityModel
from ..models.num_of_actions_model import NumOfActionModel


router: APIRouter = APIRouter(prefix='/actions', tags=['actions'])


@router.get('', response_model=list[ActivityModel],
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
    return [
        ActivityModel(**activity) for activity in
        await db.get_actions(start_time=start_time, end_time=end_time)
    ]


@router.get('/num', response_model=list[NumOfActionModel],
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
    return [
        NumOfActionModel(**activity) for activity in
        await db.get_num_of_actions(start_time, end_time)
    ]


@router.get('/more', response_model=list[NumOfActionModel],
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
    return [
        NumOfActionModel(**activity) for activity in
        await db.get_more_than_actions(num, start_time, end_time)
    ]


@router.get('/related_to/{gov_id}', response_model=list[GroupedActivityModel],
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
    resonse: list[ActivityModel] = [
        ActivityModel(**a) for a in
        await db.get_actions_for_object(gov_id)
    ]

    res: list[dict] = [
        a.dict() for a in resonse
    ]

    data = json.loads(json.dumps(res))
    out: list[dict] = list()
    ids: dict[str, dict] = dict()
    actions: list[dict] = list()

    for d in data:
        id: str = d['responsible']['id']
        g_id: str = d['responsible']['governance_id']
        version: str = d['responsible']['version']
        current: str = d['responsible']['current']

        ids.update({id: d['responsible']})

        d['responsible'].update({'_id': id})
        del d['responsible']['id']
        d['responsible'].update({'_governance_id': g_id})
        del d['responsible']['governance_id']
        d['responsible'].update({'_version': version})
        del d['responsible']['version']
        d['responsible'].update({'_current': current})
        del d['responsible']['current']

        ids.update({id: d['responsible']})

        actions.append(
                        {
                            "responsible": id,
                            "name": d['name'],
                            "affected_objects": d["affected_objects"],
                            "start_time": d["start_time"],
                            "end_time": d["end_time"]
                        })

    for r in ids:
        actions_by_user: list[dict] = list()

        for a in actions:
            if r == a['responsible']:
                actions_by_user.append(
                    {
                        "name": a['name'],
                        "affected_objects": a["affected_objects"],
                        "start_time": a["start_time"],
                        "end_time": a["end_time"]
                    })

        out.append(
            {
                "responsible": ids[r],
                "actions": actions_by_user
            }
        )
    return [GroupedActivityModel(**o) for o in out]


@router.get('/grouped_by_user', response_model=list[GroupedActivityModel],
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
    res = [a.dict() for a in await get_actions(start_time, end_time)]

    data = json.loads(json.dumps(res))
    out: list[dict] = list()
    ids: dict[str, dict] = dict()
    actions: list[dict] = list()

    for d in data:
        id: str = d['responsible']['id']
        gov_id: str = d['responsible']['governance_id']
        version: str = d['responsible']['version']
        current: str = d['responsible']['current']

        ids.update({id: d['responsible']})

        d['responsible'].update({'_id': id})
        del d['responsible']['id']
        d['responsible'].update({'_governance_id': gov_id})
        del d['responsible']['governance_id']
        d['responsible'].update({'_version': version})
        del d['responsible']['version']
        d['responsible'].update({'_current': current})
        del d['responsible']['current']

        ids.update({id: d['responsible']})

        actions.append(
                        {
                            "responsible": id,
                            "name": d['name'],
                            "affected_objects": d["affected_objects"],
                            "start_time": d["start_time"],
                            "end_time": d["end_time"]
                        })

    for r in ids:
        actions_by_user: list[dict] = list()

        for a in actions:
            if r == a['responsible']:
                actions_by_user.append(
                    {
                        "name": a['name'],
                        "affected_objects": a["affected_objects"],
                        "start_time": a["start_time"],
                        "end_time": a["end_time"]
                    })

        out.append(
            {
                "responsible": ids[r],
                "actions": actions_by_user
            }
        )
    return [GroupedActivityModel(**o) for o in out]
