import logging
from time import sleep

import bson.errors
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import status as http_codes
from pymongo.errors import ConnectionFailure
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from federatedmlrest.api.routers import (users, organisations, auth,
                                         strategies, datasets, ml_models, configurations, proposals,
                                         quality_requirements, metadata, results)  # auth

from fastapi.middleware.cors import CORSMiddleware

from federatedmlrest.api.routers import groups
from federatedmlrest.lib.initializer import create_starting_data
from federatedmlrest.mongo import MongoDB
from ProvenanceMetadataNeo4J.metadata import MetadataMiddleware


logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

app = FastAPI(
    title='FML Data Governance API',
    version='1.0.0',
    docs_url='/docs',
    swagger_ui_parameters={"operationsSorter": "method"}
) 

origins = [
    "http://localhost:3000",
    "http://web-dashboard:3000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetadataMiddleware)


@app.exception_handler(bson.errors.InvalidId)
async def handle_invalid_object_ids(
    request: Request, exc: bson.errors.InvalidId,
) -> Response:
    """Pass InvalidId errors as UnprocessableEntity error to HTTPException handler."""
    handler = app.exception_handlers[HTTPException.__base__]

    return await handler(  # type: ignore
        request, HTTPException(status_code=http_codes.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)),
    )


app.include_router(groups.router)
# app.include_router(members.router)
app.include_router(strategies.router)
app.include_router(configurations.router)
app.include_router(ml_models.router)
app.include_router(datasets.router)
app.include_router(proposals.router)
app.include_router(quality_requirements.router)
app.include_router(users.router)
app.include_router(organisations.router)
app.include_router(metadata.router)
app.include_router(auth.router)  # example for basic auth
app.include_router(results.router)


@app.get('/', include_in_schema=False)
def redirect_to_ui() -> RedirectResponse:
    """Redirect from root path to swagger ui."""
    return RedirectResponse('/docs')

@app.get("/echo")
async def echo_headers(request: Request):
    return {"authorization": request.headers.get("authorization")}

if __name__ == '__main__':
    db = MongoDB(timeout_ms=500)
    db_connection = db.db
    try:
        db_connection.command('ping')
    except ConnectionFailure:
        log.warning("Connection failed: Database is not available.")
    else:
        sleep(1)
        log.info("Successfully connected to the database.")
        create_starting_data()
        uvicorn.run('federatedmlrest.main:app',
                    host="0.0.0.0",
                    port=5100,
                    reload=True,
                    forwarded_allow_ips="*",
                    root_path="/api1")
