"""
Contains constants for cypher-queries that retrieve entries
"""

ANYTHING: str = 'MATCH (a {governance_id:$gov_id}) RETURN a'

OBJECT_PREFIX: str = 'MATCH (obj {governance_id:$gov_id})'
OBJECT_POSTFIX: str = ('(ag: Agent) RETURN ag.governance_id as governance_id, '
                       'ag.version as version, '
                       'toString(ag.timestamp) as timestamp')
OBJECT_BY_ATT: str = OBJECT_PREFIX + '-[:provAttribution]->' + OBJECT_POSTFIX
OBJECT_BY_ASC: str = OBJECT_PREFIX + '-[:provAssociation]->' + OBJECT_POSTFIX
OBJECT_BY_DER: str = OBJECT_PREFIX + '-[:provDerivation]->' + OBJECT_POSTFIX
OBJECT_BY_DEL: str = OBJECT_PREFIX + '<-[:provDelegation]-' + OBJECT_POSTFIX
OBJECT_BY_GEN: str = OBJECT_PREFIX + \
    '-[:provGeneration]->(a: Activity)-[:provAssociation]->' + OBJECT_POSTFIX
OBJECT_BY_MEM: str = OBJECT_PREFIX + '<-[:provMembership]-' + OBJECT_POSTFIX

# Retrieve Agent

AGENT_BY_ID: str = ('MATCH (ag: Agent {governance_id:$ag_id}) '
                    'RETURN ag.governance_id as governance_id, '
                    'ag.version as version, '
                    'toString(ag.timestamp) as timestamp')
AGENT_BY_KIND: str = ('MATCH (ag: Agent {kind:$ag_kind}) '
                      'RETURN ag.governance_id as governance_id, '
                      'ag.version as version, '
                      'toString(ag.timestamp) as timestamp')
AGENT_BY_ID_KIND: str = ('MATCH (ag: Agent '
                         '{governance_id:$ag_id, kind:$ag_kind}) '
                         'RETURN ag.governance_id as governance_id, '
                         'ag.version as version, '
                         'toString(ag.timestamp) as timestamp '
                         'ORDER BY ag.version DESC LIMIT 1')
AGENT_BY_ID_KIND_VERSION: str = ('MATCH (ag: Agent '
                                 '{governance_id:$ag_id, kind:$ag_kind, '
                                 'version:$ag_version}) '
                                 'RETURN ag.governance_id as governance_id, '
                                 'ag.version as version,'
                                 'toString(ag.timestamp) as timestamp')
AGENT_CURRENT_VERSION: str = ('MATCH (ag: Agent '
                              '{governance_id:$ag_id, kind:$ag_kind}) '
                              'RETURN ag.version '
                              'ORDER BY ag.version DESC LIMIT 1')

# Retrieve Entities

ENTITY_BY_ID: str = ('MATCH (ent: Entity {governance_id:$ent_id}) '
                     'RETURN ent.governance_id as governance_id, '
                     'ent.version as version, '
                     'toString(ent.timestamp) as timestamp')
ENTITY_BY_KIND: str = ('MATCH (ent: Entity {kind:$ent_kind})'
                       'RETURN ent.governance_id as governance_id, '
                       'ent.version as version, '
                       'toString(ent.timestamp) as timestamp')
ENTITY_CURRENT_VERSION: str = ('MATCH (ent: Entity '
                               '{governance_id:$ent_id, kind:$ent_kind}) '
                               'RETURN ent.version '
                               'ORDER BY ent.version DESC LIMIT 1')

QR: str = ('MATCH (s: Entity {governance_id:$s_id}) '
           'MATCH (s)<-[:provAssociation]-(q: Entity '
           '{kind:\'quality_requirement\'}) '
           'RETURN q.governance_id as governance_id, q.version as version, '
           'toString(q.timestamp) as timestamp')

# Retrieve Activities

ACTIVITY_BY_NAME: str = ('MATCH (ac: Activity {name:$ent_name}) '
                         'RETURN a.name as name, '
                         'a.affected_objects as affected_objects, '
                         'toString(a.start_time) as start_time, '
                         'toString(a.end_time) as end_time')
ACTIVITY_BY_USER: str = ('MATCH (a: Activity)-[:provAssociation]->'
                         '(ag: Agent{governance_id:$ag_id}) '
                         'WHERE datetime(a.start_time) >= datetime($st) and '
                         'datetime(a.end_time) <= datetime($et) '
                         'RETURN ag.governance_id as responsible, '
                         'a.name as name, '
                         'a.affected_objects as affected_objects, '
                         'toString(a.start_time) as start_time, '
                         'toString(a.end_time) as end_time '
                         'ORDER BY ag.governance_id, a.start_time')
ACTIVITY: str = ('MATCH (a: Activity)-[:provAssociation]->(ag: Agent) '
                 'WHERE datetime(a.start_time) >= datetime($st) and '
                 'datetime(a.end_time) <= datetime($et)'
                 'RETURN ag.governance_id as responsible, a.name as name, '
                 'a.affected_objects as affected_objects, '
                 'toString(a.start_time) as start_time, '
                 'toString(a.end_time) as end_time '
                 'ORDER BY ag.governance_id, a.start_time')
ACTIVITY_COUNT: str = ('MATCH (a: Activity)-[:provAssociation]->(ag: Agent)'
                       'WHERE datetime(a.start_time) >= datetime($st) and '
                       'datetime(a.end_time) <= datetime($et)'
                       'RETURN ag.governance_id as responsible, '
                       'count(ag) as num_of_actions '
                       'ORDER BY ag.governance_id')
ACTIVITY_MORE: str = ('MATCH (a: Activity)-[:provAssociation]->(ag: Agent) '
                      'WHERE datetime(a.start_time) >= datetime($st) and '
                      'datetime(a.end_time) <= datetime($et) '
                      'WITH ag.governance_id as gov_id, '
                      'count(ag.governance_id) as action_count '
                      'WHERE action_count >= $num '
                      'RETURN gov_id as responsible, '
                      'action_count as num_of_actions '
                      'ORDER BY gov_id')
ACTIVITY_OBJ: str = ('MATCH (obj {governance_id:$gov_id})--(a: Activity)'
                     '-[:provAssociation]->(ag: Agent) '
                     'RETURN ag.governance_id as responsible, a.name as name, '
                     'a.affected_objects as affected_objects, '
                     'toString(a.start_time) as start_time, '
                     'toString(a.end_time) as end_time')

# Retrieve Users

USERS_IN_GROUP: str = ('MATCH (ag: Agent {kind:\'user\'})-[:provMembership]->'
                       '(ent: Entity {governance_id:$ent_id ,kind:\'group\'}) '
                       'RETURN ag.governance_id as governance_id, '
                       'ag.version as version, '
                       'toString(ag.timestamp) as timestamp '
                       'ORDER BY ag.governance_id')

# Retrieve Configurations

CONFIGURATIONS_FOR_STRATEGY: str = ('MATCH (ent1: Entity '
                                    '{kind:\'configuration\'})'
                                    '-[:provAssociation]->'
                                    '(ent2: Entity {governance_id:$ent_id, '
                                    'kind:\'strategy\'}) '
                                    'RETURN ent1.governance_id as '
                                    'governance_id, ent1.version as version, '
                                    'toString(ent1.timestamp) as timestamp '
                                    'ORDER BY ent1.governance_id')

# Root Cause Analysis Query
# Please see the documentation in docs/configuration_root_cause_analysis.md for more details.
CONFIGURATION_ROOT_CAUSE_GRAPH: str = (
    # Step 1: Get the current configuration and find the cutoff timestamp from previous config in same strategy
    'MATCH (config:Entity {governance_id:$config_id, kind:\'configuration\'}) '
    'OPTIONAL MATCH (config)-[:provAssociation]->(strategy:Entity {kind:\'strategy\'}) '
    # Find all strategies with the same governance_id (all versions of the same logical strategy)
    'OPTIONAL MATCH (same_strategy:Entity {kind:\'strategy\', governance_id: strategy.governance_id}) '
    # Find all configurations linked to any version of this strategy
    'OPTIONAL MATCH (prev_config:Entity {kind:\'configuration\'})-[:provAssociation]->(same_strategy) '
    'WHERE datetime(prev_config.timestamp) < datetime(config.timestamp) '
    'WITH config, '
    'CASE '
        'WHEN count(prev_config) > 0 '
        'THEN max(prev_config.timestamp) '
        'ELSE null '
    'END as cutoff_timestamp '
    # Step 2: Get the configuration and its direct relationships
    'OPTIONAL MATCH (config)-[:provAssociation]->(strategy:Entity {kind:\'strategy\'}) '
    'OPTIONAL MATCH (dataset:Entity {kind:\'dataset\'})-[:provAssociation]->(config) '
    'OPTIONAL MATCH (model:Entity {kind:\'ml-model\'})-[:provAssociation]->(config) '
    'OPTIONAL MATCH (proposal:Entity {kind:\'proposal\'})-[:provAssociation]->(strategy) '
    'OPTIONAL MATCH (vote:Entity {kind:\'vote\'})-[:provAssociation]->(proposal) '
    # Step 3: Collect unique governance IDs for all entity types
    'WITH config, config.governance_id as config_id, cutoff_timestamp, '
    'COLLECT(DISTINCT strategy.governance_id) as strategy_ids, '
    'COLLECT(DISTINCT dataset.governance_id) as dataset_ids, '
    'COLLECT(DISTINCT model.governance_id) as model_ids, '
    'COLLECT(DISTINCT proposal.governance_id) as proposal_ids, '
    'COLLECT(DISTINCT vote.governance_id) as vote_ids '
    # Step 4: Get entities and activities with temporal filtering
    'UNWIND (strategy_ids + dataset_ids + model_ids + proposal_ids + vote_ids + [config_id]) as entity_id '
    'MATCH (entity:Entity {governance_id: entity_id}) '
    'WHERE CASE '
        'WHEN cutoff_timestamp IS NULL '
        'THEN datetime(entity.timestamp) <= datetime(config.timestamp) '
        'ELSE datetime(entity.timestamp) >= datetime(cutoff_timestamp) AND datetime(entity.timestamp) <= datetime(config.timestamp) '
    'END '
    # Step 5: Get Related Agents and Activities
    'OPTIONAL MATCH (entity)-[:provAttribution]->(creator:Agent) '
    'OPTIONAL MATCH (entity)-[:provGeneration]->(activity:Activity) '
    'WHERE activity IS NULL OR '
    'activity.affected_objects CONTAINS config_id OR '
    'CASE '
        'WHEN cutoff_timestamp IS NULL '
        'THEN datetime(activity.start_time) <= datetime(config.timestamp) '
        'ELSE datetime(activity.start_time) >= datetime(cutoff_timestamp) AND datetime(activity.start_time) <= datetime(config.timestamp) '
    'END '
    'OPTIONAL MATCH (activity)-[:provAssociation]->(responsible:Agent) '
    # Step 6: Return Results
    'RETURN COLLECT(DISTINCT {entity: entity, creator: creator}) as entities_with_creators, '
    'COLLECT(DISTINCT {activity: activity, responsible: responsible}) as activities_with_agents'
)
