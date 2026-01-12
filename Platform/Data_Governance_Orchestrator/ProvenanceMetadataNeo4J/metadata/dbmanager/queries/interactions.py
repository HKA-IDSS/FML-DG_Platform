"""
Contains constants for cypher-queries that execute interactions not fitting
into the other files
"""

ADD_USER_TO_GROUP: str = ('MATCH (ag1: Agent {governance_id:$ag_add_id, '
                          'version:$ag_add_version})'
                          'MATCH (ag2: Agent {governance_id:$ag_res_id, '
                          'version:$ag_res_version})'
                          'MATCH (ent: Entity {governance_id:$ent_id, '
                          'version:$ent_version})'
                          'CREATE (group: Entity {governance_id:$ent_id, '
                          'version:$new_version, kind:\'group\', '
                          'timestamp:$g_time})'
                          'CREATE (a: Activity {name:$a_name, '
                          'affected_objects:$a_aff, '
                          'start_time:$a_stime, end_time:$a_etime})'
                          'CREATE (ag1)-[:provMembership]->(group)'
                          'CREATE (a)-[:provAssociation]->(ag2)'
                          'CREATE (group)-[:provDerivation]->(ent)'
                          'CREATE (group)-[:provAttribtion]->(ag2)'
                          'CREATE (group)-[:provGeneration]->(a)')


END_VOTING: str = ('MATCH (ag: Agent {governance_id:$ag_id, '
                   'version:$ag_version})'
                   'MATCH (p: Entity {governance_id:$p_id})'
                   'CREATE (a: Activity {name:$a_name, '
                   'affected_objects:$a_aff, start_time:$a_stime, '
                   'end_time:$a_etime})'
                   'CREATE (a)-[:provAssociation]->(ag)'
                   'CREATE (a)-[:provAssociation]->(p)')
