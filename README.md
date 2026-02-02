# FML-DG_Platform
The Federated Machine Learning Data Governance (FML-DG) platform presents a platform for FL with Data Governance mechanisms following the paper: A Platform to Integrate Data Governance in Federated Learning. The project was developed under the Aura.ai project (https://www.h-ka.de/idss/aura-ai).

## Overall Structure

## Setup

### Platform

For the platform, there three steps for setting up the whole platform.
1. Run the minio sh file placed in the Platform folder by executing the following command (in the platform folder):
```shell
sh ./run_minio.sh
```
2. F


#### Additional Configuration: Keycloak

The Keycloak component requires additional steps to make it work for the platform. Once the docker containers are 
running, access the Keycloak administration console in [http://localhost:8080](http://localhost:8080). Then, perform the
following configuration steps:

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

