from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/proposals', tags=['proposals'])


@router.get('', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Return all proposals as a JSON.'
                }
})
async def get_all_proposals() -> list[EntityModel]:
    return [EntityModel(**proposal) for proposal in db.get_all_proposals()]
