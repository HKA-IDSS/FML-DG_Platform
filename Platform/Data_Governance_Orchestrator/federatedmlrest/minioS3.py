import io
import os
from pathlib import Path
from typing import Optional
from uuid import UUID

import yaml

from minio import Minio


class MinioS3:
    _minio_connection: Minio
    _bucket_name: str = "datagovernanceorchestrator"

    def __init__(self, path=None, timeout_ms: Optional[int] = None):
        if path:
            config_path = path
        else:
            config_path = Path(os.path.dirname(__file__)) / 'config.yml'

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            url = config["minioconfig"]["dburl"]
            port = config["minioconfig"]["port"]
            access_key = config["minioconfig"]["accesskey"]
            secret_key = config["minioconfig"]["secretkey"]

        self._minio_connection = Minio(
            url + port,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )

    def get_minio_connection(self):
        return self._minio_connection

    def get_dataframe(self, configuration_id, metric_name):
        response = self._minio_connection.get_object(self._bucket_name,
                                                     str(configuration_id) + "/dataframes/" + metric_name)
        return response.data

    def save_dataframe(self, configuration_id: UUID, metric_name: str, dataframe):
        # Upload data with content-type.

        self._minio_connection.put_object(
            self._bucket_name,
            str(configuration_id) + "/dataframes/" + metric_name + ".csv",
            io.BytesIO(dataframe),
            length=len(dataframe),
            content_type="application/csv",
        )

    def get_model(self, configuration_id, type_of_model):
        if type_of_model == "XGBoost":
            final_string = "xgboost_model.json"
        else:
            final_string = "mlp_model.keras"
        response = self._minio_connection.get_object(self._bucket_name,
                                                     str(configuration_id) + "/models/" + final_string)
        return response.data

    def save_models(self, configuration_id: UUID, type_of_model: str, model):
        # Upload data with content-type.
        if type_of_model == "XGBoost":
            final_string = "xgboost_model.json"
        else:
            final_string = "mlp_model.keras"
        self._minio_connection.put_object(
            self._bucket_name,
            str(configuration_id) + "/models/" + final_string,
            io.BytesIO(model),
            length=len(model),
            content_type="application/octet-stream"
        )

