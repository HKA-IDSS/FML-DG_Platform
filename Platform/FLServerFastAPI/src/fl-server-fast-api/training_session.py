import asyncio
import logging
import random
import subprocess
import sys
from functools import reduce
from typing import Dict, Any

import fastapi
from fastapi import FastAPI, WebSocket, Depends, APIRouter
from tensorflow.python.ops.gen_data_flow_ops import barrier

from common import Tags, PyUUID, MongoID
from flower_server.util import OptunaConnection

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # self.active_connections: dict[PyUUID, list[WebSocket]] = {}
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_text(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    # async def send_personal_message(self, message: str, websocket: WebSocket):
    #     await websocket.send_text(message)

    async def broadcast_json(self, message: Any):
        for connection in self.active_connections:
            await connection.send_json(message)


class TrainingSession:
    configuration_id: PyUUID
    possible_group_members: list[PyUUID]
    # possible_group_members: int
    current_group_members: list[PyUUID]
    members_who_do_not_want_to_participate: [PyUUID]
    model_final_name: str
    compute_shapley_values: bool
    connection_ip: str

    strategy: str

    dataset_name: str
    dataset: dict
    dataset_input_size: int
    dataset_output_size: int

    model: str
    model_hyperparameters: list

    metric_names: list[str]

    rounds: int
    hyperparameter_search: bool
    hyperparameter_search_rounds: int
    current_hyperparameters_rounds_run: int

    process_running: bool
    lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, configuration_dict):
        self.configuration_id = configuration_dict["configuration_id"]
        self.possible_group_members = configuration_dict["group_members"]
        self.number_clients = configuration_dict["number_clients"]
        self.current_group_members = []
        self.model_final_name = configuration_dict["configuration_id"]
        self.compute_shapley_values = configuration_dict["compute_shapley_values"]
        # self.connection_ip = configuration_dict["connection_ip"]

        self.strategy = configuration_dict["strategy"]
        self.dataset_name = configuration_dict["dataset"]
        self.dataset_schema_validation_info = configuration_dict["validation_configuration"]
        self.hashes_of_valid_datasets: Dict[str, str] = {}  # Key: Client_id, Value: Hash_Dataset
        self.dataset_input_size = configuration_dict["dataset_input_size"]
        self.dataset_output_size = configuration_dict["dataset_output_size"]
        self.model = configuration_dict["model"]

        if self.dataset_output_size > 1:
            self.metric_names = [
                "CrossEntropyLoss",
                "Accuracy",
                "F1ScoreMacro",
                "F1ScoreMicro",
                "MCC"
            ]
        else:
            # Not yet implemented.
            self.metric_names = []

        self.rounds = configuration_dict["rounds"]
        self.hyperparameter_search = configuration_dict["hyperparameter_search"]
        self.hyperparameter_space = configuration_dict["hyperparameter_space"]
        self.hyperparameter_search_rounds = configuration_dict["hyperparameter_search_rounds"]
        self.current_hyperparameters_rounds_run = 0

        self.load_best_trial = 0
        self.compute_shapley_values = configuration_dict["compute_shapley_values"]

        if self.hyperparameter_search:
            _ = OptunaConnection.optuna_create_study(self.model_final_name, ["minimize"])
        else:
            self.hyperparameter_search_rounds = 0

        self.process_running = False
        self.last_round_check: bool = False
        # self.subscription_into_training = asyncio.Barrier(len(self.possible_group_members))
        self.subscription_into_training = asyncio.Barrier(self.number_clients)
        self.participants_barrier = asyncio.Barrier(1)

        self.connection_manager = ConnectionManager()
        # self.connection_port = str(int(2000 * random.random()) + 54000)
        self.connection_port = "54000"
        self.connection_ip = "localhost:" + self.connection_port

    async def update_barrier(self, number_of_active_participants: int):
        async with self.lock:
            self.participants_barrier = asyncio.Barrier(number_of_active_participants)

    async def get_training_parameters(self):
        training_parameters = {
            "strategy": self.strategy,
            "name_dataset": self.dataset_name,
            "model_selected": self.model,
            # "client_number": str(1),
            "connection_ip": self.connection_ip,
            "metric_name": self.metric_names
        }

        return training_parameters

    async def get_flower_server(self):
        await self.participants_barrier.wait()
        async with self.lock:
            if not self.process_running:
                self.last_round_check = self.current_hyperparameters_rounds_run == self.hyperparameter_search_rounds
                if self.last_round_check:
                    load_best_trial = 1
                    shapley_values = self.compute_shapley_values
                else:
                    load_best_trial = 0
                    shapley_values = 0

                subprocess.Popen(['python',
                                  'src/fl-server-fast-api/flower_server/Server.py',
                                  self.connection_port,
                                  self.strategy,
                                  str(self.dataset_schema_validation_info["dataset_features"][-1]["valid_values"]),
                                  self.model,
                                  str(self.hyperparameter_space),
                                  str(self.dataset_input_size),
                                  str(self.dataset_output_size),
                                  str(self.number_clients),
                                #   str(self.number_clients),
                                  str(self.rounds),
                                  reduce(lambda metric1, metric2: metric1 + "-" + metric2, self.metric_names),
                                  self.model_final_name,
                                  str(load_best_trial),
                                  str(shapley_values),
                                  str(self.configuration_id)],
                                 shell=False,
                                 stdout=sys.stdout)
                self.process_running = True
                print("Starting process")
                self.current_hyperparameters_rounds_run += 1
                print(f"Current round: {self.current_hyperparameters_rounds_run}")
                await asyncio.sleep(3)
                await self.participants_barrier.reset()
        return self.last_round_check

    async def claim_training_finished(self):
        self.process_running = False

    # number_clients: int


class TrainingManager:
    current_trainings: Dict[str, TrainingSession]

    def __init__(self):
        self.current_trainings = {}

#
# router = APIRouter(prefix="/training_sessions", tags=[Tags.TRAINING_SESSIONS])
