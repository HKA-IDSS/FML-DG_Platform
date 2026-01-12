from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/dev',
                              tags=['dev'])


@router.post('/reset', responses={
                status.HTTP_200_OK: {
                    'description': 'Deletes all database entries'
                }
            })
async def reset() -> dict:
    """
    deletes all database entries
    """
    db.reset()
    return {'message': 'database has been reset'}
