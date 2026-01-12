# type: ignore
import json

from datetime import datetime
from typing import Any

import httpx

from neo4j import GraphDatabase, Session, Driver, Record

from .. import const as c
from ..token import get_token
from .exceptions.group_does_not_exist import GroupDoesNotExistException
from .exceptions.object_does_not_exist import ObjectDoesNotExistException
from .exceptions.relationship_does_not_exist import (
    RelationshipDoesNotExistException
)
from .exceptions.strategy_does_not_exist import StrategyDoesNotExistException
from .exceptions.user_does_not_exist import UserDoesNotExistException
from .exceptions.version_does_not_exist import VersionDoesNotExistException
from .queries import (
    create as cr,
    delete as de,
    update as u,
    retrieve as rtr,
    interactions as inter
)


class Neo4JConnection:
    """
    Manages access to the metadata database
    """
    _driver: Driver
    _session: Session
    _uri: str
    _auth: tuple | None
    _database: str | None

    def __init__(self,
                 uri: str,
                 authorization: tuple | None = None,
                 database: str | None = None
                 ) -> None:
        """
        Constructor for Neo4JConnection, creates connection to the database
        :param uri: address of database
        :param authorization: tuple for authorization in form
                              (username, password)
        :param database: name of the database to be accessed
        """
        self._driver = GraphDatabase.driver(uri=uri,
                                            auth=authorization,
                                            database=database)
        self._session = self._driver.session(database=database)
        self._uri = uri
        self._auth = authorization
        self._database = database

    ###########################################################################
    ###########################################################################
    # basic functions                                                         #
    ###########################################################################
    ###########################################################################

    def reconnect(self) -> None:
        """
        Connects the Neo4JConnection to the database
        """
        if not self._driver.verify_connectivity():
            self._driver = GraphDatabase.driver(uri=self._uri,
                                                auth=self._auth,
                                                database=self._database)
            self._session = self._driver.session(database=self._database)

    def close(self) -> None:
        """
        Close Session and disconnect from Database
        """
        self._session.close()
        self._driver.close()

    ###########################################################################
    ###########################################################################
    # auxiliary functions                                                     #
    ###########################################################################
    ###########################################################################

    def reset(self) -> bool:
        """
        Deletes all database entries
        :returns: bool whether the operation was successful
        """
        try:
            self._driver.execute_query(de.RESET)
            return True
        except Exception:
            return False

    def __exists(self, governance_id: str) -> bool:
        """
        Returns if an entry with the given id exists
        :param governance_id: g_id of the object
        :returns: if an entry with the given id exists
        """
        return len(
            self._driver.execute_query(rtr.ANYTHING,
                                       gov_id=governance_id
                                       ).records
                   ) > 0

    async def __retrieve_user_dict(self, gov_id: str) -> dict | None:
        """
        retrieves the user dict for the given id
        :param gov_id: id of the user
        :returns: dict of user info
        """
        token: str | None = await get_token()
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f'{c.REST_URL}/users/{gov_id}',
                    headers={'Authorization': token}
                )
                if res.status_code == httpx.codes.OK:
                    return res.json()
                else:
                    return None
        except Exception:
            return None

    def __create_agent(self, governance_id: str, kind: str) -> bool:
        """
        Creates a database entry for an agent
        :param governance_id: g_id of the agent
        :returns: bool whether the operation was successful
        """
        try:
            rec: list[Record] = self._driver.execute_query(
                rtr.AGENT_BY_ID, ag_id=governance_id).records
            if len(rec) == 0:
                self._driver.execute_query(cr.AGENT,
                                           ag_kind=kind,
                                           ag_id=governance_id,
                                           ag_version=1,
                                           ag_time=datetime.now())
            else:
                self._driver.execute_query(u.AGENT,
                                           ag_kind=kind,
                                           ag_id=governance_id,
                                           ag_version=len(rec) + 1,
                                           ag_time=datetime.now(),
                                           old_version=len(rec))
            return True
        except Exception:
            return False

    def __create_entity(self, governance_id: str, kind: str) -> bool:
        """
        Creates a database entry for an entity
        :param governance_id: g_id of the entity
        :returns: bool whether the operation was successful
        """
        try:
            rec: list[Record] = self._driver.execute_query(rtr.ENTITY_BY_ID,
                                                           ent_id=governance_id
                                                           ).records
            if len(rec) == 0:
                self._driver.execute_query(cr.ENTITY,
                                           ent_kind=kind,
                                           ent_id=governance_id,
                                           ent_version=1,
                                           ent_time=datetime.now())
            else:
                self._driver.execute_query(u.ENTITY,
                                           ent_kind=kind,
                                           ent_id=governance_id,
                                           ent_version=len(rec) + 1,
                                           ent_time=datetime.now(),
                                           old_version=len(rec))
            return True
        except Exception:
            return False

    def __create_activity(self, name: str) -> bool:
        """
        Creates a database entry for an activity
        :param name: name of the activity
        :returns: bool whether the operation was successful
        """
        try:
            self._driver.execute_query(cr.ACTIVITY,
                                       a_name=name,
                                       a_stime=datetime.now(),
                                       a_etime=datetime.now())
            return True
        except Exception:
            return False

    def __get_current_version(self, gov_id: str, kind: str) -> Any:
        """
        Returns the current version of a given entity
        :param gov_id: g_id of the entity
        :param kind: kind of the entity
        :returns: the current version of the entity
        """
        if kind == 'user' or kind == 'organisation':
            return self._driver.execute_query(rtr.AGENT_CURRENT_VERSION,
                                              ag_id=gov_id,
                                              ag_kind=kind
                                              ).records[0].value()

        else:
            return self._driver.execute_query(rtr.ENTITY_CURRENT_VERSION,
                                              ent_id=gov_id,
                                              ent_kind=kind
                                              ).records[0].value()

    ###########################################################################
    ###########################################################################
    # functions used by the metadata api                                      #
    ###########################################################################
    ###########################################################################

    def get_all_users(self) -> list[dict]:
        """
        Returns a list of all users
        :returns: list of all users
        """
        return self._session.run(rtr.AGENT_BY_KIND, ag_kind='user').data()

    def get_user(self,
                 governance_id: str,
                 version: int | None = None
                 ) -> list[dict]:
        """
        Returns either the current or specified version of a user
        :param governance_id: g_id of the user
        :param version: version of the user; optional
        :returns: user
        :raises: UserDoesNotExistException if user_id is not an existing user
        :raises: VersionDoesNotExistException if version of user does not exist
        """
        if not self.__exists(governance_id):
            raise UserDoesNotExistException(
                f'User {governance_id} does not exist in the database.'
            )
        if version:
            res: list[dict] = self._session.run(rtr.AGENT_BY_ID_KIND_VERSION,
                                                ag_id=governance_id,
                                                ag_kind='user',
                                                ag_version=version
                                                ).data()
            if len(res) == 0:
                raise VersionDoesNotExistException(
                    f'Version {version} of {governance_id} does not exist')
            return res
        else:
            return self._session.run(rtr.AGENT_BY_ID_KIND,
                                     ag_id=governance_id,
                                     ag_kind='user'
                                     ).data()

    def get_all_organisations(self) -> list[dict]:
        """
        Returns all organisations
        :returns: list of all organisations
        """
        return self._session.run(rtr.AGENT_BY_KIND,
                                 ag_kind='organisation'
                                 ).data()

    def get_all_groups(self) -> list[dict]:
        """
        Returns all groups
        :returns: list of all groups
        """
        return self._session.run(rtr.ENTITY_BY_KIND, ent_kind='group').data()

    def get_members_of_group(self, group_id: str) -> list[dict]:
        """
        retrieves user in group and returns them in a list
        :param group_id: g_id of the group
        :returns: list of all users
        :raises: GroupDoesNotExistException if the group does not exist
        """
        if not self.__exists(group_id):
            raise GroupDoesNotExistException(
                f'Group {group_id} does not exist in the metadata database.'
            )
        return self._session.run(rtr.USERS_IN_GROUP, ent_id=group_id).data()

    def get_all_models(self) -> list[dict]:
        """
        Returns all models as a list
        :returns: list of all models
        """
        return self._session.run(rtr.ENTITY_BY_KIND,
                                 ent_kind='ml-model'
                                 ).data()

    def get_all_datasets(self) -> list[dict]:
        """
        Returns all datasets as a list
        :returns: list of all groups
        """
        return self._session.run(rtr.ENTITY_BY_KIND, ent_kind='dataset').data()

    def get_configurations(self) -> list[dict]:
        """
        Returns all configurations as a list
        :returns: list of all configurations
        :raises: StrategyDoesNotExistException if strategy_id does not exist
        """
        return self._session.run(rtr.ENTITY_BY_KIND,
                                 ent_kind='configuration'
                                 ).data()

    def get_all_strategies(self) -> list[dict]:
        """
        Returns all strategies for a given group as a list
        :returns: list of all configurations
        """
        return self._session.run(rtr.ENTITY_BY_KIND,
                                 ent_kind='strategy'
                                 ).data()

    def get_all_proposals(self) -> list[dict]:
        """
        Returns all proposals as a list
        :returns: list of all proposal
        """
        return self._session.run(rtr.ENTITY_BY_KIND,
                                 ent_kind='proposal'
                                 ).data()

    def get_qr_for_strategy(self, strategy_id: str) -> list[dict]:
        """
        Returns all qrs for the strategy as a list
        :param strategy_id: id of the strategy
        :returns: list of qrs
        """
        return self._session.run(rtr.QR, s_id=strategy_id).data()

    async def get_actions(self,
                          user_id: str | None = None,
                          start_time: datetime | None = None,
                          end_time: datetime | None = None,
                          fetch_user_info: bool = True
                          ) -> list[dict]:
        """
        Returns all actions taken by a user if one is given. Can include all
        information about the user.
        If a start_time is given then it will return all actions taken since
        If an end_time is given it will return all actions taken until
        If both a start and end_time are given all actions in that interval
        will be returned
        :param user_id: id of the user
        :param start_time: start of interval
        :param end_time: end of interval
        :param fetch_user_info: whether the user info shall be retrieved
        :returns: list of all actions + information about user if desired
        :raises: UserDoesNotExistException if user_id is not an existing user
        """
        out: list[dict] = list()
        start_time = start_time if start_time else datetime(1900, 1, 1)
        end_time = end_time if end_time else datetime.now()

        if user_id:
            if not self.__exists(user_id):
                raise UserDoesNotExistException(
                    f'User {user_id} does not exist in the metadata database.')

            out = self._session.run(rtr.ACTIVITY_BY_USER,
                                    ag_id=user_id,
                                    st=start_time,
                                    et=end_time
                                    ).data()
        else:
            out = self._session.run(rtr.ACTIVITY,
                                    st=start_time,
                                    et=end_time
                                    ).data()

        if fetch_user_info:
            lookup_table: dict[str, dict] = dict()
            for entry in out:
                id: str = entry['responsible']
                if id in lookup_table:
                    entry['responsible'] = lookup_table[id]
                else:
                    user: dict | None = await self.__retrieve_user_dict(id)
                    if user:
                        lookup_table.update({id: user})
                        entry['responsible'] = user
                    else:
                        lookup_table.update({id: {'_governance_id': id}})
                        entry['responsible'] = {'_governance_id': id}
        return out

    async def get_num_of_actions(self,
                                 start_time: datetime | None = None,
                                 end_time: datetime | None = None
                                 ) -> list[dict]:
        """
        returns map of user: number of actions taken within the given interval
        :param num: number of actions
        :param start_time: start of interval
        :param end_time: end of interval
        :returns:  map of user and number of actions
        """
        start_time = start_time if start_time else datetime(1900, 1, 1)
        end_time = end_time if end_time else datetime.now()
        out = self._session.run(rtr.ACTIVITY_COUNT,
                                st=start_time,
                                et=end_time
                                ).data()
        lookup_table: dict[str, dict] = dict()
        for entry in out:
            id: str = entry['responsible']
            if id in lookup_table:
                entry['responsible'] = lookup_table[id]
            else:
                user: dict | None = await self.__retrieve_user_dict(id)
                if user:
                    lookup_table.update({id: user})
                    entry['responsible'] = user
                else:
                    lookup_table.update({id: {'_governance_id': id}})
                    entry['responsible'] = {'_governance_id': id}
        return out

    async def get_more_than_actions(self, num: int,
                                    start_time: datetime | None = None,
                                    end_time: datetime | None = None
                                    ) -> list[dict]:
        """
        returns a map of user and number of actions taken within the given
        interval for all user that have taken more than num actions
        :param start_time: start of interval
        :param end_time: end of interval
        :returns: a map of user and number of actions taken within the given
                  interval for all user that have taken more than num actions
        """
        start_time = start_time if start_time else datetime(1900, 1, 1)
        end_time = end_time if end_time else datetime.now()
        out = self._session.run(rtr.ACTIVITY_MORE,
                                num=num,
                                st=start_time,
                                et=end_time
                                ).data()
        lookup_table: dict[str, dict] = dict()
        for entry in out:
            id: str = entry['responsible']
            if id in lookup_table:
                entry['responsible'] = lookup_table[id]
            else:
                user: dict | None = await self.__retrieve_user_dict(id)
                if user:
                    lookup_table.update({id: user})
                    entry['responsible'] = user
                else:
                    lookup_table.update({id: {'_governance_id': id}})
                    entry['responsible'] = {'_governance_id': id}
        return out

    async def get_actions_for_object(self, gov_id: str) -> list[dict]:
        """
        returns all actions related to the object
        :param gov_id: id of the object
        :raises: ObjectDoesNotExistException if gov_id is invalid
        :returns: list of activities
        """
        if not self.__exists(gov_id):
            raise ObjectDoesNotExistException(
                f'Object {gov_id} does not exist in the metadata database.'
            )
        out: list[dict] = self._session.run(rtr.ACTIVITY_OBJ,
                                            gov_id=gov_id
                                            ).data()
        lookup_table: dict[str, dict] = dict()
        for entry in out:
            id: str = entry['responsible']
            if id in lookup_table:
                entry['responsible'] = lookup_table[id]
            else:
                user: dict | None = await self.__retrieve_user_dict(id)
                if user:
                    lookup_table.update({id: user})
                    entry['responsible'] = user
                else:
                    lookup_table.update({id: {'_governance_id': id}})
                    entry['responsible'] = {'_governance_id': id}
        return out

    def get_nodes_by_relationship(self,
                                  gov_id: str,
                                  relationship: str
                                  ) -> list[dict]:
        """
        returns all objects associated with the given object via the given
        relationship
        :param gov_id: id of the object
        :param relationship: type of relationship
        :returns: list of all objects associated with the given activity
        :raises: ObjectDoesNotExistException if gov_id is invalid
        :raises: RelationshipDoesNotExistException if relationship is invalid
        """
        if not self.__exists(gov_id):
            raise ObjectDoesNotExistException(
                f'Object {gov_id} does not exist in the metadata database.'
            )
        match relationship:
            case 'attribution':
                return self._session.run(rtr.OBJECT_BY_ATT,
                                         gov_id=gov_id
                                         ).data()
            case 'association':
                return self._session.run(rtr.OBJECT_BY_ASC,
                                         gov_id=gov_id
                                         ).data()
            case 'delegation':
                return self._session.run(rtr.OBJECT_BY_DEL,
                                         gov_id=gov_id
                                         ).data()
            case 'derivation':
                return self._session.run(rtr.OBJECT_BY_DER,
                                         gov_id=gov_id
                                         ).data()
            case 'generation':
                return self._session.run(rtr.OBJECT_BY_GEN,
                                         gov_id=gov_id
                                         ).data()
            case 'membership':
                return self._session.run(rtr.OBJECT_BY_MEM,
                                         gov_id=gov_id
                                         ).data()
            case _:
                raise RelationshipDoesNotExistException(
                    f'Relationship {relationship} does not exist.')

    ###########################################################################
    ###########################################################################
    # functions for the middleware                                            #
    ###########################################################################
    ###########################################################################

    def create_organisation(self, governance_id: str) -> bool:
        """
        Creates a database entry for an organisation
        :param governance_id: g_id of the organisation
        :returns: bool whether the operation was successful
        """
        return self.__create_agent(governance_id, 'organisation')

    def create_user(self,
                    governance_id: str,
                    organisation_id: str,
                    user_id: str) -> bool:
        """
        Creates a database entry for a user
        :param governance_id: g_id of the user
        :param user_id: id of the user that creates the user
        :returns: bool whether the operation was successful
        """
        if not self.__exists(user_id):
            self.__create_agent(user_id, 'user')
        if not self.__exists(organisation_id):
            return False
        rec: list[Record] = self._driver.execute_query(
                rtr.AGENT_BY_ID, ag_id=governance_id).records
        try:
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.AGENT_INTERACTION,
                    res_id=user_id,
                    res_version=self.__get_current_version(user_id, 'user'),
                    org_id=organisation_id,
                    org_version=self.__get_current_version(organisation_id,
                                                           'organisation'),
                    ag_kind='user',
                    ag_id=governance_id,
                    ag_version=1,
                    ag_time=datetime.now(),
                    a_name='create_user',
                    a_aff=json.dumps({"user": governance_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.AGENT,
                    res_id=user_id,
                    res_version=self.__get_current_version(user_id, 'user'),
                    ag_id=governance_id,
                    ag_version=len(rec) + 1,
                    ag_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_user',
                    a_aff=json.dumps({"user": governance_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
                return True
        except Exception:
            return False

    def create_group(self, group_id: str, user_id: str) -> bool:
        """
        Creates a database entry for a  or updates it if it already exists
        :param group_id: g_id of the group
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(user_id):
                self.__create_agent(user_id)
            rec: list[Record] = self._driver.execute_query(
                rtr.ENTITY_BY_ID, ent_id=group_id).records
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.GROUP,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='group',
                    ent_id=group_id,
                    ent_version=1,
                    ent_time=datetime.now(),
                    a_name='create_group',
                    a_aff=json.dumps({"group": group_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='group',
                    ent_id=group_id,
                    ent_version=len(rec) + 1,
                    ent_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_group',
                    a_aff=json.dumps({"group": group_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            return True
        except Exception:
            return False

    def add_user_to_group(self,
                          group_id: str,
                          user_res: str,
                          user_add: str
                          ) -> bool:
        """
        adds a user to group
        :param group_id: g_id of the group
        :param user_add: g_id of the user to be added
        :param user_res: g_id of the user responsible
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(group_id) or not self.__exists(user_add):
                return False
            self._driver.execute_query(
                inter.ADD_USER_TO_GROUP,
                ag_add_id=user_add,
                ag_add_version=self.__get_current_version(user_add, 'user'),
                ag_res_id=user_res,
                ag_res_version=self.__get_current_version(user_res, 'user'),
                ent_id=group_id,
                ent_version=self.__get_current_version(group_id, 'group'),
                new_version=self.__get_current_version(group_id, 'group') + 1,
                g_time=datetime.now(),
                a_name='add_user_to_group',
                a_aff=json.dumps({"user": user_add, "group": group_id}),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def create_model(self, model_id: str, user_id: str) -> bool:
        """
        Creates a database entry for a model
        :param model_id: g_id of the group
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(user_id):
                return False
            rec: list[Record] = self._driver.execute_query(
                rtr.ENTITY_BY_ID, ent_id=model_id).records
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='ml-model',
                    ent_id=model_id,
                    ent_version=1,
                    ent_time=datetime.now(),
                    a_name='create_model',
                    a_aff=json.dumps({"ml-model": model_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='ml-model',
                    ent_id=model_id,
                    ent_version=len(rec) + 1,
                    ent_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_model',
                    a_aff=json.dumps({"ml-model": model_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            return True
        except Exception:
            return False

    def create_dataset(self, dataset_id: str, user_id: str) -> bool:
        """
        Creates a database entry for a dataset
        :param dataset_id: g_id of the dataset
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(user_id):
                return False
            rec: list[Record] = self._driver.execute_query(
                rtr.ENTITY_BY_ID, ent_id=dataset_id).records
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='dataset',
                    ent_id=dataset_id,
                    ent_version=1,
                    ent_time=datetime.now(),
                    a_name='create_dataset',
                    a_aff=json.dumps({"dataset": dataset_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(
                        user_id, 'user'),
                    ent_kind='dataset',
                    ent_id=dataset_id,
                    ent_version=len(rec) + 1,
                    ent_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_dataset',
                    a_aff=json.dumps({"dataset": dataset_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            return True
        except Exception:
            return False

    def create_strategy(self,
                        strategy_id: str,
                        group_id: str,
                        user_id: str
                        ) -> bool:
        """
        Creates a database entry for a strategy or updates it
        :param strategy_id: g_id of the strategy
        :param group_id: g_id of the group this strategy is assigned to
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(group_id) or not self.__exists(user_id):
                return False
            rec: list[Record] = self._driver.execute_query(
                rtr.ENTITY_BY_ID, ent_id=strategy_id).records
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.STRATEGY,
                    g_id=group_id,
                    g_version=self.__get_current_version(group_id, 'group'),
                    new_version=self.__get_current_version(group_id,
                                                           'group') + 1,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='strategy',
                    ent_id=strategy_id,
                    ent_version=1,
                    ent_time=datetime.now(),
                    a_name='create_strategy',
                    a_aff=json.dumps({"strategy": strategy_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='strategy',
                    ent_id=strategy_id,
                    ent_version=len(rec) + 1,
                    ent_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_strategy',
                    a_aff=json.dumps({"strategy": strategy_id}),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            return True
        except Exception:
            return False

    def add_quality_requirement(self,
                                qr_id: str,
                                strategy_id: str,
                                user_id: str
                                ) -> bool:
        """
        Adds a quality requirement to the given strategy
        :param qr_id: g_id of the quality requirement
        :param strategy_id: g_id of the strategy this qr is assigned to
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(strategy_id) or not self.__exists(user_id):
                return False
            self._driver.execute_query(
                cr.QUALITY_REQUIREMENT,
                ag_id=user_id,
                ag_version=self.__get_current_version(user_id, 'user'),
                str_id=strategy_id,
                str_version=self.__get_current_version(strategy_id,
                                                       'strategy'),
                ent_kind='quality_requirement',
                ent_id=qr_id,
                ent_version=1,
                ent_time=datetime.now(),
                a_name=('add_quality_requirement_to_strategy'),
                a_aff=json.dumps({
                                    "quality_requirement": qr_id,
                                    "strategy": strategy_id
                                 }),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
        except Exception:
            return False

    def add_configuration(self,
                          config_id: str,
                          strategy_id: str,
                          group_id: str,
                          model_id: str,
                          dataset_id: str,
                          user_id: str) -> bool:
        """
        Creates a database entry for a configuration
        :param config_id: g_id of the configuration
        :param strategy_id: g_id of the strategy this configuration is assigned
                            to
        :param group_id: g_id of the group this strategy is assigned to
        :param model_id: g_id of the model this configuration is assigned to
        :param dataset_id: g_id of the dataset this configuration is assigned
                           to
        :param user_id: g_id of the user
        :returns: bool whether the operation was successful
        """
        try:
            if (not self.__exists(strategy_id) or not self.__exists(model_id)
                    or not self.__exists(group_id)
                    or not self.__exists(dataset_id)
                    or not self.__exists(user_id)):
                return False
            rec: list[Record] = self._driver.execute_query(
                rtr.ENTITY_BY_ID, ent_id=config_id).records
            if len(rec) == 0:
                self._driver.execute_query(
                    cr.CONFIGURATION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    str_id=strategy_id,
                    str_version=self.__get_current_version(strategy_id,
                                                           'strategy'),
                    model_id=model_id,
                    model_version=self.__get_current_version(model_id,
                                                             'ml-model'),
                    dataset_id=dataset_id,
                    dataset_version=self.__get_current_version(dataset_id,
                                                               'dataset'),
                    ent_kind='configuration',
                    ent_id=config_id,
                    ent_version=1,
                    ent_time=datetime.now(),
                    a_name=('add_configuration_to_strategy'),
                    a_aff=json.dumps({
                                    "configuration": config_id,
                                    "strategy": strategy_id
                                 }),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            else:
                self._driver.execute_query(
                    u.ENTITY_INTERACTION,
                    ag_id=user_id,
                    ag_version=self.__get_current_version(user_id, 'user'),
                    ent_kind='configuration',
                    ent_id=config_id,
                    ent_version=len(rec) + 1,
                    ent_time=datetime.now(),
                    old_version=len(rec),
                    a_name='update_configuration',
                    a_aff=json.dumps({
                                    "configuration": config_id,
                                    "strategy": strategy_id
                                 }),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
            return True
        except Exception:
            return False

    def create_proposal(self,
                        proposal_id: str,
                        strategy_id: str,
                        user_id: str
                        ) -> bool:
        """
        Creates a new proposal for the given strategy
        :param proposal_id: id of the new proposal
        :param strategy_id: id of the strategy
        :param user_id: id of the user
        :returns: bool whether the operation was successful
        """
        if not self.__exists(strategy_id) or not self.__exists(user_id):
            return False
        try:
            self._driver.execute_query(
                cr.PROPOSAL,
                ag_id=user_id,
                ag_version=self.__get_current_version(user_id, 'user'),
                str_id=strategy_id,
                str_version=self.__get_current_version(strategy_id,
                                                       'strategy'),
                ent_kind='proposal',
                ent_id=proposal_id,
                ent_version=1,
                ent_time=datetime.now(),
                a_name='create_proposal',
                a_aff=json.dumps({"proposal": proposal_id}),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def vote(self, proposal_id: str, vote: str, user_id: str) -> bool:
        """
        logs a vote
        :param proposal_id: id of the proposal
        :param vote: vote of the user
        :param user_id: id of the user
        :returns: bool whether the operation was successful
        """
        if not self.__exists(proposal_id) or not self.__exists(user_id):
            return False
        try:
            self._driver.execute_query(
                cr.VOTE,
                ag_id=user_id,
                ag_version=self.__get_current_version(user_id, 'user'),
                prop_id=proposal_id,
                prop_version=1,
                ent_kind='vote',
                ent_id=f"{proposal_id}_vote_{user_id}",
                ent_version=1,
                ent_time=datetime.now(),
                a_name=f'voted',
                a_aff=json.dumps({"proposal": proposal_id}),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def delete_entry(self, gov_id: str, user_res: str, type: str) -> bool:
        """
        deletes an entry
        :param gov_id: id of the object to be deleted
        :param user_res: responsible user
        :param type: kind of deleted object
        :returns: bool whether the operation was successful
        """
        try:
            self._driver.execute_query(
                de.DEL,
                governance_id=gov_id,
                ag_id=user_res,
                ag_version=self.__get_current_version(user_res),
                a_name=f'deleted_{type}',
                a_aff=json.dumps({type: gov_id}),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def delete_vote(self, prop_id: str, voter_id, user_res: str) -> bool:
        """
        deletes a vote
        :param prop_id: id of the proposal
        :param voter_id: id of the voter
        :param user_res: responsible user
        :returns: bool whether the operation was successful
        """
        try:
            self._driver.execute_query(
                de.VOTE,
                prop_id=prop_id,
                voter_id=voter_id,
                ag_id=user_res,
                ag_version=self.__get_current_version(user_res),
                a_name=f'deleted_vote',
                a_aff=json.dumps({"vote": f"{prop_id}_vote_{voter_id}"}),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def update_config(type: str,
                      config_id: str,
                      model_id: str,
                      dataset_id: str,
                      user_res: str) -> bool:
        """
        updates either the model or the dataset of a config
        :param config_id: id of the config
        :param model_id: id of the model
        :param dataset_id: id of the dataset
        :user_res: id of the responsible user
        :returns: bool whether the operation was successful
        """
        if type == '/mlmodel':
            try:
                self._driver.execute_query(
                    u.CONFIG_MODEL,
                    ag_id=user_res,
                    ag_version=self.__get_current_version(user_res),
                    c_id=config_id,
                    nm_id=model_id,
                    nm_version=self.__get_current_version(model_id),
                    a_name=f'update_model_of_config',
                    a_aff=json.dumps({
                                    "configuration": config_id,
                                    "ml-model": model_id
                                 }),

                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
                return True
            except Exception:
                return False
        elif type == '/dataset':
            try:
                self._driver.execute_query(
                    u.CONFIG_D_SET,
                    ag_id=user_res,
                    ag_version=self.__get_current_version(user_res),
                    c_id=config_id,
                    nd_id=dataset_id,
                    nd_version=self.__get_current_version(dataset_id),
                    a_name=f'update_dataset_of_config',
                    a_aff=json.dumps({
                                    "configuration": config_id,
                                    "dataset": dataset_id
                                 }),
                    a_stime=datetime.now(),
                    a_etime=datetime.now()
                )
                return True
            except Exception:
                return False
        else:
            return False

    def end_voting(self,
                   strategy_id: str,
                   proposal_id: str,
                   type: str,
                   user_res: str
                   ) -> bool:
        """
        ends the voting
        :param strategy_id: id of the strategy related to the proposal
        :param proposal_id: id of the proposal
        :param type: type of proposal
        :param user_res: id of the responsible user
        :returns: success
        """
        try:
            self._driver.execute_query(
                inter.END_VOTING,
                ag_id=user_res,
                ag_version=self.__get_current_version(user_res, 'user'),
                p_id=proposal_id,
                a_name=f'end_voting',
                a_aff=json.dumps({
                                "proposal": proposal_id,
                                "strategy": strategy_id
                             }),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def track_evaluation_results_upload(self,
                                       configuration_id: str,
                                       filename: str,
                                       user_id: str) -> bool:
        """
        Tracks the upload of evaluation results
        :param configuration_id: g_id of the configuration
        :param filename: name of the uploaded file
        :param user_id: g_id of the user uploading
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(user_id) or not self.__exists(configuration_id):
                return False
            
            # Create a unique entity ID for this evaluation result
            entity_id = f"{configuration_id}_evaluation_{filename}"
            
            self._driver.execute_query(
                cr.ENTITY_INTERACTION,
                ag_id=user_id,
                ag_version=self.__get_current_version(user_id, 'user'),
                ent_kind='evaluation_result',
                ent_id=entity_id,
                ent_version=1,
                ent_time=datetime.now(),
                a_name='upload_evaluation_results',
                a_aff=json.dumps({
                    "configuration": configuration_id,
                    "filename": filename,
                    "type": "evaluation_results"
                }),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    def track_trained_model_upload(self,
                                  configuration_id: str,
                                  filename: str,
                                  user_id: str) -> bool:
        """
        Tracks the upload of a trained model
        :param configuration_id: g_id of the configuration
        :param filename: name of the uploaded file
        :param user_id: g_id of the user uploading
        :returns: bool whether the operation was successful
        """
        try:
            if not self.__exists(user_id) or not self.__exists(configuration_id):
                return False
            
            # Create a unique entity ID for this trained model
            entity_id = f"{configuration_id}_model_{filename}"
            
            self._driver.execute_query(
                cr.ENTITY_INTERACTION,
                ag_id=user_id,
                ag_version=self.__get_current_version(user_id, 'user'),
                ent_kind='trained_model',
                ent_id=entity_id,
                ent_version=1,
                ent_time=datetime.now(),
                a_name='upload_trained_model',
                a_aff=json.dumps({
                    "configuration": configuration_id,
                    "filename": filename,
                    "type": "trained_model"
                }),
                a_stime=datetime.now(),
                a_etime=datetime.now()
            )
            return True
        except Exception:
            return False

    async def get_configuration_root_cause(self, config_id: str) -> dict:
        """
        Get the root cause analysis for a configuration - traces back everything 
        that led to its creation, including all versions of related entities.
        
        :param config_id: ID of the configuration to analyze
        :returns: Dictionary containing the root cause analysis results with embedded agent info
        :raises: ObjectDoesNotExistException if configuration doesn't exist
        """
        if not self.__exists(config_id):
            raise ObjectDoesNotExistException(
                f'Configuration {config_id} does not exist in the metadata database.'
            )
        
        # Execute graph traversal query
        results = self._session.run(
            rtr.CONFIGURATION_ROOT_CAUSE_GRAPH,
            config_id=config_id
        ).data()
        
        if not results or not results[0]:
            return {
                'configuration_id': config_id,
                'entities_involved': [],
                'activities': [],
                'total_entities': 0,
                'total_activities': 0
            }
        
        result = results[0]
        
        # Process entities with their creators
        entities = []
        seen_entities = set()
        
        for entity_data in result.get('entities_with_creators', []):
            if entity_data and entity_data.get('entity'):
                entity = entity_data['entity']
                creator = entity_data.get('creator')
                
                # Handle different types of governance_id (string, int, bool)
                gov_id = entity.get('governance_id')
                if gov_id is None:
                    continue
                    
                # Convert to string for consistency
                gov_id_str = str(gov_id) if not isinstance(gov_id, str) else gov_id
                
                entity_dict = {
                    'governance_id': gov_id_str,
                    'kind': entity.get('kind'),
                    'version': entity.get('version'),
                    'timestamp': str(entity.get('timestamp', '')),
                    'created_by': creator.get('governance_id') if creator else None
                }
                
                entity_key = (entity_dict['governance_id'], entity_dict['version'])
                if entity_key not in seen_entities:
                    entities.append(entity_dict)
                    seen_entities.add(entity_key)
        
        # Process activities with their responsible agents
        activities = []
        seen_activities = set()
        
        for activity_data in result.get('activities_with_agents', []):
            if activity_data and activity_data.get('activity'):
                activity = activity_data['activity']
                responsible = activity_data.get('responsible')
                
                activity_dict = {
                    'name': activity.get('name'),
                    'affected_objects': activity.get('affected_objects', '{}'),
                    'start_time': str(activity.get('start_time', '')),
                    'end_time': str(activity.get('end_time', '')),
                    'responsible': responsible.get('governance_id') if responsible else None
                }
                
                activity_key = (activity_dict['name'], activity_dict['start_time'])
                if activity_key not in seen_activities:
                    activities.append(activity_dict)
                    seen_activities.add(activity_key)
        
        # Sort entities by kind and version, activities by start_time
        entities.sort(key=lambda x: (x.get('kind', ''), x.get('governance_id', ''), x.get('version', 0)))
        activities.sort(key=lambda x: x.get('start_time', ''))
        
        return {
            'configuration_id': config_id,
            'entities_involved': entities,
            'activities': activities,
            'total_entities': len(entities),
            'total_activities': len(activities)
        }
