# Data_Governance_Full_Stack

This repository integrates the [Cockpit](https://github.com/JsAntoPe/Data_Governance_Cockpit.git) and the [Web Dashboard](https://github.com/JsAntoPe/Web_Dashboard.git) into one master-repo and offers a [docker-compose.yml](./docker-compose.yml) to start up the whole project using [Docker](https://docker.com).

## Pulling the git modules

> The submodules are configured to be pulled via https. If this repository is pulled via SSH and https is not configured on your machine, this can cause issues.

The configured git modules can be checked out here: [.gitmodules](./.gitmodules)

Run the following commands to pull everything.

```sh
# clone this repository
git clone https://github.com/JsAntoPe/Data_Governance_Full_Stack.git
cd Data_Governance_Full_Stack
# pull submodules
git submodule init
git submodule update
```

## Start docker compose environment

> You can get docker & compose with [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Be aware that changes inside the cockpit or dashboard code wont have an effect unless you rebuild their containers. Both repositories offer a description on how to start their service to support live recompiling. The container must be stopped when running the service separately.

```sh
docker compose build --no-cache
docker compose up -d
```

## Metadata Coverage Analysis

The metadata coverage script analyzes how comprehensively the provenance metadata system tracks API operations. This script compares the API endpoints defined in the Data Governance Cockpit with the operation patterns configured in the ProvenanceMetadataNeo4J middleware to identify gaps in metadata tracking coverage.

The script works by extracting all API endpoints from the FastAPI router files, then matching them against the regex patterns defined in the metadata middleware operations. It generates a detailed report showing which endpoints are successfully tracked, which ones are missing coverage, and which tracking patterns are unused.

To run the coverage analysis, execute the script from the repository root:

```sh
python check_metadata_coverage.py
```
