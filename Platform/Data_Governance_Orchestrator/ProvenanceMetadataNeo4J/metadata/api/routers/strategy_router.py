from fastapi import APIRouter
from starlette import status

from ..database_connection import db_connection as db
from ..models.entity_models import EntityModel

router: APIRouter = APIRouter(prefix='/strategies', tags=['strategies'])


@router.get('', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all strategies as a JSON.'
                }
})
async def get_all_strategies() -> list[EntityModel]:
    """
    Returns all strategies
    """
    return [EntityModel(**strategy) for strategy in db.get_all_strategies()]


@router.get('/{id}/qr', response_model=list[EntityModel],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Returns all qualtiy requirements for the '
                                   'given strategy as a JSON.'
                }
})
async def get_qr(id: str) -> list[EntityModel]:
    """
    Returns all strategies
    """
    return [EntityModel(**strategy) for strategy in db.get_qr_for_strategy(id)]
