"""
contains constants used by the middleware and api
"""

# if true use local version of constants else use docker variants

LOCAL: bool = False

# Constants for the authorization in kc

KC_URL: str = 'http://127.0.0.1:8080' if LOCAL else 'http://kc:8080/auth' # With reverse proxy, auth needs to be added.
KC_REALM: str = 'fml'
KC_TOKEN_URL: str = f'{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/token'

KC_GRANT_TYPE: str = 'password'
KC_USERNAME: str = 'admin'
KC_PASSWORD: str = 'hkakeycloak'
KC_CLIENT_ID: str = 'fml-api'
KC_CLIENT_SECRET: str = 'qhwXVzDfriZ7hb9wRAxycxeES9C1ppLb'

KC_AUTH_CREDENTIALS: dict = {
    'grant_type': KC_GRANT_TYPE,
    'username': KC_USERNAME,
    'password': KC_PASSWORD,
    'client_id': KC_CLIENT_ID,
    'client_secret': KC_CLIENT_SECRET
}

# neo4j constants

NEO4J_URL: str = 'neo4j://127.0.0.1:7687' if LOCAL else 'neo4j://neo4j:7687'
NEO4J_USERNAME: str = 'neo4j'
NEO4J_PASSWORD: str = 'provenance-dg'
NEO4J_AUTH: tuple = (NEO4J_USERNAME, NEO4J_PASSWORD)
NEO4J_DATABASE: str = 'neo4j'

# rest-api

REST_URL: str = 'http://127.0.0.1:5100' if LOCAL else 'http://rest-api:5100/api1'

# metadata api

API_HOST: str = '0.0.0.0'
API_PORT: int = 5001
