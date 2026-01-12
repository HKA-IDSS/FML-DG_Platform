from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/ml-models', tags=['ml-models'])


@router.get('', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all ml-models as a JSON.'
                }
})
async def get_all_models() -> list[EntityModel]:
    """
    returns all ml-models
    :return: JSON-response of all ml-models
    """
    return [EntityModel(**model) for model in db.get_all_models()]
