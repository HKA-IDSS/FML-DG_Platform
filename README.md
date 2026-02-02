# FML-DG_Platform
The Federated Machine Learning Data Governance (FML-DG) platform presents a platform for FL with Data Governance mechanisms following the paper: A Platform to Integrate Data Governance in Federated Learning. The project was developed under the Aura.ai project (https://www.h-ka.de/idss/aura-ai).

## Disclaimer

This repository was used for diverse experiments conducted with the collaboration of Professors of the University of 
Cádiz. Some settings have been modified, like the connection ips of the different components, as well as the secrets of
different components. At the moment, all secrets and passwords are hardcoded within the architecture, in order to make
the reproduction of the architecture locally as straightforward as possible. Therefore, the platform is not production
ready, and multiple settings need to be performed for preparing to production. These steps were considered beyond the
scope of the work.

## Overall Structure

The FML-DG platform, as well as the experiment settings can be divided in the following structure.

```
FML-DG-Platform
├── ClientForFlower
│   ├── FLTrainingExperimentsClient1
│   ├── FLTrainingExperimentsClient2
│   └── FLTrainingExperimentsClient3
├── ClientsForPlatform
│   ├── FLClient1
│   ├── FLClient2
│   └── FLClient3
├── FLTrainingExperimentsServer
├── Platform
├── FlowerInstructions.md
└── PlatformInstructions.md
```

The platform is fully located in the Platform folder, which contains all components as well as a docker compose file
to run everything. At the moment, the different components of the platform are receiving updates, which will be included
in future updates.

The folder FLTrainingExperimentsServer contains the Flower server, which runs using poetry for reproducibility. Only
code subject to change might be ip. It is currently configured to run locally.

Finally, the clients for the platform and the flower server are in their respective folders. Each folders contains the
directory with the three clients, are the experiments were conducted in groups of three.

## Setup

### Platform

For the platform, there three steps for setting up the whole platform.
1. Run the minio sh file placed in the Platform folder by executing the following command (in the platform folder):
```shell
sh ./run_minio.sh
```
2. Run the docker compose within the main folder with the command:

```shell
docker compose up --build -d
```

3. Follow the additional configuration section for Keycloak below.

[//]: # (#### Additional Configuration: Keycloak)

The Keycloak component requires additional steps to make it work for the platform. Once the docker containers are 
running, access the Keycloak administration console in [http://localhost:8080](http://localhost:8080). Connect to it using the following
credentials (they are defined in the docker compose file):
- Username: hkakeycloak
- password: hkakeycloak

Then, perform the following configuration steps:

1. First, go into the Realms selector, at the top left, and select the fml realm.
2. Finally, we also add two redirect URLs to the following clients:
   1. In Clients -> fml-webapp -> Valid redirect uri's, add [http://localhost/*]().
3. There, add the audience for the Data_Governance_Orchestrator (fml-api) and the FLServerFastAPI 
(fml-orchestrator-docker-api), by following the steps below:
   1. Go to Clients -> fml-webapp -> Go to Client scopes -> click on fml-webapp-dedicated 
   (or fl-client-dedicated).
   2. Click on Add mapper -> By Configuration, and click on *Audience*.
   3. In the Audience window, give a name to it (recommended *Audience*), and select fml-api.
   4. Now go to Clients -> flower-server -> Go to Client scopes -> click on flower-server-dedicated
   5. Click on Add mapper -> By Configuration, and click on *Audience*.
   6. In the Audience window, give a name to it (recommended *Audience*), and select fml-api.
   7. Finally, go to Clients -> fl-client -> Go to Client scopes -> click on fl-client-dedicated
   8. Click on Add mapper -> By Configuration, and click on *Audience*.
   9. In the Audience window, give a name to it (recommended *Audience*), and select fml-orchestrator-docker-api.
4. We need to create an *admin* user within Keycloak, and add it to the admin group, which should already exist. 
For this:
   1. Create an admin in the tab users -> create user.
   2. Give the name admin
   3. Add it to the admin group, and by clicking *Join Group*, and selecting the admin group.
   4. Then, in the tab *credentials*, add a password of your choice.
5. Finally, for the client fml-api, we need to enable options for user management. For this:
   1. Go to Clients -> fml-api
   2. Go to the Service Account Roles tab
   3. Click on Assign Role -> Client roles
   4. Search for *manage-users*, and select the option.

### Flower Federated Framework

No specific setup required from the Flower Server.

## Usage

### Platform

To use the platform, follow these steps (this usage considers that you are running the platform locally):

1. First, go to [http://localhost](http://localhost).
2. Login as an admin with the credentials that were set up during the Keycloak setup.
3. Use the Admin page to create organizations and users. The organizations have only a representative meaning,
but the users can be used for those participating in the experiments. The credentials will be as follows:
   - Username: (Username that was given by the admin)
   - Password: password.

### Flower Federated Framework

To set up the Flower Server, run the following command within the folder _FLTrainingExperimentsServer_:
```shell
poetry run python src\fl-training-experiments\Client.py
```


