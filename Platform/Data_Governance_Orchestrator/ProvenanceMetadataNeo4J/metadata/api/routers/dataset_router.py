from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/datasets', tags=['datasets'])


@router.get('', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Return all datasets as a JSON.'
                }
})
async def get_all_datasets() -> list[EntityModel]:
    """
    returns all datasets
    :return: JSON-response of all datasets
    """
    return [EntityModel(**dataset) for dataset in db.get_all_datasets()]
