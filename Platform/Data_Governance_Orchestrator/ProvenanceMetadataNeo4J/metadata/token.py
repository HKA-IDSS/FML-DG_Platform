from datetime import datetime, timedelta

import httpx

from . import const as c

"""
stores the token required for requests to the Data Governance Cockpit
"""

token: str | None = None
timestamp: datetime = datetime(1900, 1, 1)


async def get_token() -> str | None:
    """
    retrieves a token to access the API
    :returns: token or None in case of error
    """
    global token
    global timestamp

    time_since_last_token: timedelta = datetime.now() - timestamp
    if time_since_last_token.total_seconds() < 270:
        return token

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(c.KC_TOKEN_URL, data=c.KC_AUTH_CREDENTIALS)
            token_rcv: str = 'Bearer ' + res.json()['access_token']
            token = token_rcv
            timestamp = datetime.now()
            return token_rcv
    except Exception:
        return None
