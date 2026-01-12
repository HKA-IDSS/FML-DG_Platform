from uuid import UUID

import fastapi
from fastapi import File, UploadFile
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_codes
from fastapi.responses import PlainTextResponse, StreamingResponse
from pymongo.database import Database
from starlette.responses import Response
import pandas as pd

from federatedmlrest.api import dependencies, errors
from federatedmlrest.api.models import group_models, strategy_models, config_models, ml_model_models, results_models, result_models
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.api.models.result_models import AddTrainingConfigurationInformation
from federatedmlrest.api.tags import Tags
from federatedmlrest.keycloak_auth import get_current_user, keycloak_user_in_group, require_user_in_group
from federatedmlrest.lib import getters
from federatedmlrest.api.DBConnection import get_minio_s3, get_db
from federatedmlrest.mongo import Collections

router = APIRouter(prefix="/results", tags=[Tags.RESULTS])


@router.get(
    '/evaluation/test/{metric}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_test_result_dataframe(
    metric: str,
    token: dict = Depends(get_current_user),
) -> PlainTextResponse:
    """Get all datasets."""
    # configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    # strategy = getters.find_strategy_governance(configuration.strategy_linked)
    # require_user_in_group(str(strategy.belonging_group))

    with open("federatedmlrest/files_for_testing/Evaluation_"+ metric +".csv", "rb") as f:
        dataframe = f.read()
    # dataframe = pd.read_csv("federatedmlrest/files_for_testing/Evaluation_Accuracy.csv", index_col=0)
    return PlainTextResponse(dataframe, media_type="text/csv")


@router.get(
    '/shapley_value/test/{metric}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_test_result_dataframe(
    metric: str,
    token: dict = Depends(get_current_user),
) -> PlainTextResponse:
    """Get all datasets."""
    # configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    # strategy = getters.find_strategy_governance(configuration.strategy_linked)
    # require_user_in_group(str(strategy.belonging_group))

    # with open("federatedmlrest/files_for_testing/SV_"+ metric +".csv", "rb") as f:
    #     dataframe = f.read()
    dataframe = pd.read_csv("federatedmlrest/files_for_testing/SV_Accuracy.csv")
    summed_dataframe = dataframe.groupby(["Evaluator"]).sum(numeric_only=True)
    summed_dataframe.drop("Round", axis=1, inplace=True)
    return PlainTextResponse(summed_dataframe.to_csv(), media_type="text/csv")


@router.get(
    '/training_information/{configuration_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_training_information(
    configuration_id: PyUUID,
    token: dict = Depends(get_current_user),
) -> result_models.TrainingConfigurationInformation:
    """Get all datasets."""
    configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    strategy = getters.find_strategy_governance(configuration.strategy_linked)
    require_user_in_group(str(strategy.belonging_group))

    training_configuration_information = getters.find_results_training_information_governance(configuration_id)
    return training_configuration_information


@router.get(
    '/evaluation/{configuration_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_result_dataframe(
    configuration_id: UUID,
    metric_name: str,
    token: dict = Depends(get_current_user),
) -> PlainTextResponse:
    """Get all datasets."""
    configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    strategy = getters.find_strategy_governance(configuration.strategy_linked)
    require_user_in_group(str(strategy.belonging_group))

    minio = get_minio_s3()
    try:
        dataframe = minio.get_dataframe(configuration_id, "Evaluation_" + metric_name + ".csv")
    except Exception as ex:
        raise (HTTPException(status_code=http_codes.HTTP_404_NOT_FOUND))
    return PlainTextResponse(dataframe, media_type="text/csv")


@router.get(
    '/shapley_values/{configuration_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_sv_dataframe(
    configuration_id: UUID,
    metric_name: str,
    token: dict = Depends(get_current_user),
) -> PlainTextResponse:
    """Get all datasets."""
    configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    strategy = getters.find_strategy_governance(configuration.strategy_linked)
    require_user_in_group(str(strategy.belonging_group))

    minio = get_minio_s3()
    try:
        dataframe = minio.get_dataframe(configuration_id, "SV_" + metric_name)
    except Exception as ex:
        raise (HTTPException(status_code=http_codes.HTTP_404_NOT_FOUND))
    summed_dataframe = dataframe.groupby(["Evaluator"]).sum(numeric_only=True)
    summed_dataframe.drop("Round", axis=1, inplace=True)
    return PlainTextResponse(summed_dataframe, media_type="text/csv")


@router.get(
    '/models/{configuration_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a file in bytestream.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=None,
    response_model_exclude_none=True,
)
async def get_model(
    configuration_id: UUID,
    model_type: str = "MLP",
    # configuration: config_models.Configuration = Depends(dependencies.get_configuration),
    token: dict = Depends(get_current_user),
) -> Response:
    configuration = getters.find_config(dependencies.transform_to_pyuuid(str(configuration_id)))
    strategy = getters.find_strategy_governance(configuration.strategy_linked)
    require_user_in_group(str(strategy.belonging_group))

    minio = get_minio_s3()
    model = minio.get_model(configuration_id, model_type)
    if model_type == "XGBoost":
        return Response(model,
                        media_type="application/json",
                        headers={'Content-Disposition': 'attachment; filename="model.json"'})
    else:
        return Response(model,
                        media_type="application/octet-stream",
                        headers={'Content-Disposition': 'attachment; filename="model.keras"'})


@router.post(
    '/training_information',
    responses={
        http_codes.HTTP_201_CREATED: {
            'description': 'Returns an accept from the operation.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=str,
    response_model_exclude_none=True,
)
async def upload_training_information(
    add_results_information: AddTrainingConfigurationInformation,
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> str:
    """Post results."""
    results_information_dict = result_models.TrainingConfigurationInformation(**add_results_information.dict()).dict(exclude_none=True, by_alias=True)
    db[Collections.RESULTS].insert_one(results_information_dict)
    return "The file was successfully uploaded"


@router.post(
    '/evaluations/{configuration_id}',
    responses={
        http_codes.HTTP_201_CREATED: {
            'description': 'Returns an accept from the operation.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=results_models.FileUploadResponse,
    response_model_exclude_none=True,
)
async def upload_results_dataframe(
    file: UploadFile,
    configuration_id: UUID,
    # group: group_models.Group = Depends(dependencies.get_group),
    # strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
    token: dict = Depends(get_current_user),
) -> results_models.FileUploadResponse:
    """Post results."""
    contents = file.file.read() # The file is received as bytes.
    minio = get_minio_s3()
    minio.save_dataframe(configuration_id, file.filename, contents)

    return results_models.FileUploadResponse(
        message="The file was successfully uploaded",
        filename=file.filename,
        _governance_id=str(configuration_id),
        file_type="evaluation_results"
    )


@router.post(
    '/models/{configuration_id}',
    responses={
        http_codes.HTTP_201_CREATED: {
            'description': 'Returns an accept from the operation.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The file was not found.',
        },
    },
    response_model=results_models.FileUploadResponse,
    response_model_exclude_none=True,
)
async def upload_trained_model(
    file: UploadFile,
    configuration_id: UUID,
    token: dict = Depends(get_current_user),
) -> results_models.FileUploadResponse:
    """Post results."""
    contents = file.file.read()  # The file is received as bytes.
    minio = get_minio_s3()
    minio.save_models(configuration_id, file.filename, contents)

    return results_models.FileUploadResponse(
        message="The file was successfully uploaded",
        filename=file.filename,
        _governance_id=str(configuration_id),
        file_type="trained_model"
    )