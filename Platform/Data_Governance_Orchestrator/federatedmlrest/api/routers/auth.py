import fastapi
from fastapi import Depends
from federatedmlrest.keycloak_auth import get_current_user

router = fastapi.APIRouter(
    prefix='/auth',
    tags=['Test'],
)


@router.get('/')
def test_basic_auth(username: str = Depends(get_current_user)):
    """Example how to use basic auth dependncy."""
    return {'username': username}
