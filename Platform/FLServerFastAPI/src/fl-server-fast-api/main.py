import json
import logging
from typing import Any, List, Dict

import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, APIRouter, Response, UploadFile, HTTPException
from fastapi import status as http_codes
from keycloak_auth import get_current_user, verify_token
from common import PyUUID
from training_session import TrainingSession, TrainingManager

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

training_manager = TrainingManager()
#
# @app.websocket("/ws-test")
# async def ws_test(websocket: WebSocket):
#     logger.info("WS HANDLER HIT")
#     auth_header = websocket.headers.get("Authorization")
#
#     if not auth_header or not auth_header.startswith("Bearer "):
#         await websocket.close(code=1008)
#         return
#
#     token = auth_header.split(" ", 1)[1]
#
#     try:
#         payload = await verify_token(token)
#     except HTTPException:
#         await websocket.close(code=1008)
#         return
#
#     logger.info("WS HANDLER HIT AFTER AUTH")
#     await websocket.accept()
#     await websocket.send_text("ok")
#     await websocket.close()

@app.post("/upload_configuration",
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the IDs of the training sessions.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'No training sessions found.',
        },
    },
    response_model=None)
async def load_training_session(configuration_file: Dict[Any, Any]):
    training_manager.current_trainings[configuration_file["configuration_id"]] = TrainingSession(configuration_file)


@app.get(
    "/training_sessions",
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the IDs of the training sessions.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'No training sessions found.',
        },
    },
    response_model=None
)
async def get_available_training_sessions(
    _ = Depends(get_current_user)
) -> List[str]:
    training_sessions_ids: List[str] = [str(id) for id in training_manager.current_trainings.keys()]
    return training_sessions_ids


@app.websocket("/register_dataset/{configuration_id}")
async def register_dataset(
        websocket: WebSocket,
        configuration_id: PyUUID
):
    logger.info(websocket.headers)
    try:
        logger.info(websocket.headers)
        auth_header = websocket.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            await websocket.close(code=1008)
            return

        token = auth_header.split(" ", 1)[1]

        try:
            payload = await verify_token(token)
        except HTTPException:
            await websocket.close(code=1008)
            return

        await websocket.accept()

        user_id = payload["sub"]

        if str(configuration_id) not in training_manager.current_trainings:
            raise HTTPException(status_code=http_codes.HTTP_404_NOT_FOUND)

        training_session = training_manager.current_trainings[str(configuration_id)]

        # if user_id not in training_session.possible_group_members:
        #     await websocket.close(reason="You are not allowed to participate in this training session.")
        # else:
        #     await websocket.send_bytes(training_session.dataset_schema_validation_info)
        #     validation_result = await websocket.receive_text()
        #     print(validation_result)
        #     await websocket.close()
        await websocket.send_json(training_session.dataset_schema_validation_info)
        validation_result = await websocket.receive_text()
        if validation_result == "True":
            print("Registering Dataset")
            training_session.hashes_of_valid_datasets[user_id] = await websocket.receive_text()

        else:
            print("Registration failed. There was a problem")

        await websocket.close()
    except WebSocketDisconnect:
        print("Problem")
        await websocket.close()
    # return Response(content="Dataset was registered", media_type="text")


@app.websocket(
    "/join_training/{configuration_id}"
)
async def websocket_endpoint(
    websocket: WebSocket,
    configuration_id: PyUUID
):
    auth_header = websocket.headers.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=1008)
        return

    token = auth_header.split(" ", 1)[1]

    try:
        payload = await verify_token(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    user_id = payload["sub"]
    training_session = training_manager.current_trainings[str(configuration_id)]
    manager = training_session.connection_manager

    await manager.connect(websocket)
    await manager.send_personal_message("JoiningTraining", websocket)
    dataset_hash = training_session.hashes_of_valid_datasets[str(user_id)]
    await websocket.send_text(dataset_hash)
    print(f"Active connections: {len(manager.active_connections)}")
    await training_session.subscription_into_training.wait()
    await training_session.update_barrier(len(manager.active_connections))
    try:
        while True:
            print("Requesting client input")
            finished_stage = await websocket.receive_text()
            print("Finished_stage")
            if finished_stage == "SubscriptionFinished":
                await websocket.send_text("PerformPreprocessing")
                await websocket.send_json(training_session.dataset_schema_validation_info["dataset_features"])
            elif finished_stage == "PreprocessingFinished":
                print("SendingParameters")
                await websocket.send_text("SendingParameters")
                await websocket.receive_text()
                print("Parameters requested")
                training_params = {"strategy": training_session.strategy,
                                   "name_dataset": dataset_hash,
                                   "model_selected": training_session.model,
                                   "client_number": str(1),
                                   "connection_ip": training_session.connection_ip,
                                   "metric_name": training_session.metric_names}
                await websocket.send_json(training_params)
            elif (finished_stage == "NextRound?") or (finished_stage == "ParametersReceived"):
                print("Reaching start training")
                last_training = await training_session.get_flower_server()
                print("Next training session")
                await manager.send_personal_message("StartClient", websocket)
                training_status = "Unfinished"
                while training_status == "Unfinished":
                    training_status = await websocket.receive_text()
                print("Training finished")
                await training_session.claim_training_finished()
                print("Training claimed finished")
                if last_training:
                    print("Last training?")
                    await manager.send_personal_message("EndConnection", websocket)
                    await websocket.receive_text()
                    manager.disconnect(websocket)
                    finished_stage = "TrainingFinished"
                    training_manager.current_trainings.pop(str(configuration_id))
                    print("Closing session")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(manager.active_connections)
        await training_session.update_barrier(len(manager.active_connections))
        # await manager.broadcast_text(f"User disconnected")
