"""
Contains constants for cypher-queries that delete entries
"""
RESET: str = 'MATCH (n) DETACH DELETE n'
DEL: str = ('MATCH (obj {governance_id:$governance_id}) '
            'MATCH (ag: Agent {governance_id:$ag_id, version:$ag_version}) '
            'OPTIONAL MATCH (obj)<-[:provAssociation]-(a: Activity) '
            'CREATE (a: Activity {name:$a_name, affected_objects:$a_aff, '
            'start_time:$a_stime, end_time:$a_etime}) '
            'CREATE (a)-[:provAssociation]->(ag) '
            'DETACH DELETE obj, a')

VOTE: str = ('MATCH (p: Entity {governance_id:$prop_id, kind:\'proposal\'}) '
             'MATCH (v: Agent {governance_id:$voter_id}) '
             'MATCH (ag: Agent {governance_id:$ag_id, version:$ag_version})'
             'MATCH (p)<-[:provAssociation]-(vote: Entity)'
             '-[:provAttribution]->(v)'
             'CREATE (a: Activity {name:$a_name, affected_objects:$a_aff, '
             'start_time:$a_stime, end_time:$a_etime}) '
             'CREATE (a)-[:provAssociation]->(ag) '
             'DETACH DELETE vote')
