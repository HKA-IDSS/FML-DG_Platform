from .. import const as c

from ..dbmanager.neo4j_connection import Neo4JConnection
"""
Contains a Neo4JConnection instance that will be used by the metadata-api and
its routers
"""
db_connection: Neo4JConnection = Neo4JConnection(
    c.NEO4J_URL,
    authorization=c.NEO4J_AUTH,
    database=c.NEO4J_DATABASE
)
