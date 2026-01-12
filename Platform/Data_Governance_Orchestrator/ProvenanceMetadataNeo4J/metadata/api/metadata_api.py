import uvicorn

from fastapi import FastAPI, status
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from .. import const as c
from .database_connection import db_connection as db
from ..dbmanager.exceptions.group_does_not_exist import (
    GroupDoesNotExistException
)
from ..dbmanager.exceptions.no_actions import NoActionException
from ..dbmanager.exceptions.object_does_not_exist import (
    ObjectDoesNotExistException
)
from ..dbmanager.exceptions.relationship_does_not_exist import (
    RelationshipDoesNotExistException
)
from ..dbmanager.exceptions.strategy_does_not_exist import (
    StrategyDoesNotExistException
)
from ..dbmanager.exceptions.user_does_not_exist import (
    UserDoesNotExistException
)
from ..dbmanager.exceptions.version_does_not_exist import (
    VersionDoesNotExistException
)
from .routers import action_router as actions
from .routers import config_router as configs
from .routers import dev_router as dev
from .routers import dataset_router as datasets
from .routers import group_router as groups
from .routers import model_router as models
from .routers import organisation_router as organisations
from .routers import proposal_router as proposals
from .routers import strategy_router as strategies
from .routers import user_router as users

app = FastAPI(
    title='Metadata Database Query API',
    version='0.1'
)

app.include_router(actions.router)
app.include_router(configs.router)
app.include_router(datasets.router)
app.include_router(dev.router)
app.include_router(groups.router)
app.include_router(models.router)
app.include_router(organisations.router)
app.include_router(proposals.router)
app.include_router(strategies.router)
app.include_router(users.router)


@app.on_event('startup')
async def startup() -> None:
    db.reconnect()


@app.on_event("shutdown")
async def shutdown() -> None:
    db.close()


@app.get('/', include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse('/docs',
                            status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.exception_handler(GroupDoesNotExistException)
async def group_does_not_exist_handler(request: Request,
                                       ex: GroupDoesNotExistException
                                       ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "Group does not exist."})


@app.exception_handler(NoActionException)
async def no_actions_handler(request: Request,
                             ex: NoActionException
                             ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "User has taken no actions"})


@app.exception_handler(ObjectDoesNotExistException)
async def object_does_not_exist_handler(request: Request,
                                        ex: ObjectDoesNotExistException
                                        ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "Object does not exist."})


@app.exception_handler(RelationshipDoesNotExistException)
async def relation_does_not_exist_handler(request: Request,
                                          ex: RelationshipDoesNotExistException
                                          ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "Relationship does not exist."})


@app.exception_handler(StrategyDoesNotExistException)
async def strategy_does_not_exist_handler(request: Request,
                                          ex: StrategyDoesNotExistException
                                          ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "Strategy does not exist."})


@app.exception_handler(UserDoesNotExistException)
async def user_does_not_exist_handler(request: Request,
                                      ex: UserDoesNotExistException
                                      ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "User does not exist."})


@app.exception_handler(VersionDoesNotExistException)
async def version_does_not_exist_handler(request: Request,
                                         ex: VersionDoesNotExistException
                                         ) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content={"message": "Version of user does not exist."})


def run() -> None:
    """
    runs the metadata api
    """
    uvicorn.run(app, host=c.API_HOST, port=c.API_PORT)
