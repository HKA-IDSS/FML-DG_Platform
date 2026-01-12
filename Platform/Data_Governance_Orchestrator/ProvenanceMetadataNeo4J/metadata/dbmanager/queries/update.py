"""
Contains constants for cypher-queries that update entries
"""
AGENT: str = ('MATCH (res: Agent {governance_id:$res_id, '
              'res_version:$ag_version}) '
              'MATCH (ag_old: Agent {governance_id:$ag_id, '
              'version:$old_version})'
              'CREATE (ag: Agent {kind:$ag_kind, governance_id:$ag_id, '
              'version:$ag_version, timestamp:$ag_time})'
              'CREATE (a: Activity {name:$a_name, affected_objects:$a_aff, '
              'start_time:$a_stime, end_time:$a_etime}) '
              'CREATE (ag)-[:ProvDerivation]->(ag_old)'
              'CREATE (a)-[:provAssociation]->(ag) '
              'CREATE (ag)-[:provAttribution]->(res) '
              'CREATE (a)-[:provGeneration]->(ag)')

ENTITY: str = ('MATCH (ent_old: Entity {governance_id:$ent_id, '
               'version:$old_version})'
               'CREATE (ent: Entity {kind:$ent_kind, governance_id:$ent_id, '
               'version:$ent_version, timestamp:$ent_time})'
               'CREATE (ent)-[:provDerivation]->(ent_old)')

CONFIG_MODEL: str = ('MATCH (ag: Agent {governance_id:$ag_id, '
                     'version:$ag_version}) '
                     'MATCH (c: Entity {governance_id:$c_id, '
                     'kind:\'configuration\'}) '
                     'MATCH (c)<-[r:provAssociation]-(m: Entity '
                     '{kind:\'ml-model\'}) '
                     'MATCH (new_m: Entity {governance_id:$nm_id, '
                     'kind:\'ml-model\', version:$nm_version}) '
                     'DELETE r '
                     'CREATE (c)<-[r:provAssociation]-(new_m)'
                     'CREATE (a: Activity {name:$a_name, start_time:$a_stime, '
                     'end_time:$a_etime, affected_objects:$a_aff}) '
                     'CREATE (a)-[:provAssociation]->(ag) '
                     'CREATE (a)-[:provGeneration]->(c) '
                     'CREATE (c)-[:provGeneration]->(c)')

CONFIG_D_SET: str = ('MATCH (ag: Agent {governance_id:$ag_id, '
                     'version:$ag_version}) '
                     'MATCH (c: Entity {governance_id:$c_id, '
                     'kind:\'configuration\'}) '
                     'MATCH (c)<-[r:provAssociation]-(d: Entity '
                     '{kind:\'dataset\'}) '
                     'MATCH (new_d: Entity {governance_id:$nd_id, '
                     'kind:\'dataset\', version:$nd_version}) '
                     'DELETE r '
                     'CREATE (c)<-[r:provAssociation]-(new_d)'
                     'CREATE (a: Activity {name:$a_name, start_time:$a_stime, '
                     'end_time:$a_etime, affected_objects:$a_aff}) '
                     'CREATE (a)-[:provAssociation]->(ag) '
                     'CREATE (a)-[:provGeneration]->(c)')

# Update Interactions

ENTITY_INTERACTION: str = ('MATCH (ag: Agent {governance_id:$ag_id, '
                           'version:$ag_version}) '
                           + ENTITY
                           + 'CREATE (a: Activity {name:$a_name, '
                           'affected_objects:$a_aff, '
                           'start_time:$a_stime, end_time:$a_etime})'
                           'CREATE (ent)-[:provAttribution]->(ag)'
                           'CREATE (ent)-[:provGeneration]->(a)'
                           'CREATE (a)-[:provAssociation]->(ag)')
