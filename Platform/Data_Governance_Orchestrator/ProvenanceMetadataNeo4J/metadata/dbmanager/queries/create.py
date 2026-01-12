"""
Contains constants for cypher-queries that create entries
"""
AGENT: str = ('CREATE (ag: Agent {kind:$ag_kind, governance_id:$ag_id, '
              'version:$ag_version, timestamp:$ag_time})')
ENTITY: str = ('CREATE (ent: Entity {kind:$ent_kind, governance_id:$ent_id, '
               'version:$ent_version, timestamp:$ent_time})')
ACTIVITY: str = ('CREATE (a: Activity {name:$a_name, affected_objects:$a_aff, '
                 'start_time:$a_stime, end_time:$a_etime})')

# Create Interactions
AGENT_INTERACTION: str = ('MATCH (res: Agent {governance_id:$res_id, '
                          'version:$res_version}) '
                          'MATCH (org: Agent {governance_id:$org_id, '
                          'version:$org_version}) '
                          + AGENT + ACTIVITY
                          + 'CREATE (ag)-[:provAttribution]->(res)'
                          'CREATE (ag)-[:provGeneration]->(a)'
                          'CREATE (a)-[:provAssociation]->(res)'
                          'CREATE (ag)-[:provDelegation]->(org)')
ENTITY_INTERACTION: str = ('MATCH (ag: Agent {governance_id:$ag_id, '
                           'version:$ag_version}) '
                           + ENTITY + ACTIVITY
                           + 'CREATE (ent)-[:provAttribution]->(ag)'
                           'CREATE (ent)-[:provGeneration]->(a)'
                           'CREATE (a)-[:provAssociation]->(ag)')
GROUP: str = ENTITY_INTERACTION + 'CREATE (ag)-[:provMembership]->(ent)'
STRATEGY: str = ('MATCH (old: Entity {governance_id:$g_id, kind:\'group\', '
                 'version:$g_version})'
                 + ENTITY_INTERACTION
                 + 'CREATE (group: Entity {governance_id:$g_id, '
                 'version:$new_version, kind:\'group\', timestamp:$ent_time})'
                 'CREATE (group)-[:provAssociation]->(ent)'
                 'CREATE (group)-[:provDerivation]->(old)'
                 'CREATE (group)-[:provAttribtion]->(ag)'
                 'CREATE (group)-[:provGeneration]->(a)')
QUALITY_REQUIREMENT: str = ('MATCH (s: Entity {governance_id:$str_id, '
                            'kind:\'strategy\', version:$str_version})'
                            + ENTITY_INTERACTION
                            + 'CREATE (ent)-[:provAssociation]->(s)')
CONFIGURATION: str = ('MATCH (s: Entity {governance_id:$str_id, '
                      'kind:\'strategy\', version:$str_version})'
                      'MATCH (ds: Entity {governance_id:$dataset_id, '
                      'kind:\'dataset\', version:$dataset_version})'
                      'MATCH (mod: Entity {governance_id:$model_id, '
                      'kind:\'ml-model\', version:$model_version})'
                      + ENTITY_INTERACTION
                      + 'CREATE (ent)-[:provAssociation]->(s)'
                      'CREATE (ds)-[:provAssociation]->(ent)'
                      'CREATE (mod)-[:provAssociation]->(ent)')
PROPOSAL: str = ('MATCH (s: Entity {governance_id:$str_id, kind:\'strategy\', '
                 'version:$str_version})'
                 + ENTITY_INTERACTION
                 + 'CREATE (ent)-[:provAssociation]->(s)')
VOTE: str = ('MATCH (prop: Entity {governance_id:$prop_id, kind:\'proposal\', '
             'version:$prop_version})'
             + ENTITY_INTERACTION
             + 'CREATE (ent)-[:provAssociation]->(prop)')
