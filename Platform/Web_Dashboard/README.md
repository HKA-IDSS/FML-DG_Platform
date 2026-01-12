<br />
<div align="center">
    <a href="https://www.h-ka.de/">
        <img src="doc/img/hka_logo.jpg" alt="Logo" width="40%">
    </a>
    <h1 align="center">Web-Dashboard for Data Governance of Federated ML</h1>
    <p align="center">
        <h3>Summerterm 2025</h3>
        <br />
        Developed by Elisa Zhang, Martin Galacz & Ricardo Lauth
        <br />
        Supervised by José Antonio Peregrina Pérez & Prof. Dr. rer. nat. Christian Zirpins 
    </p>
</div>
<br />

## About The Project

This project was created in order to support the users in conducting a successful FML training by helping with the definition of governance elements, agreeing upon them and analyzing the metadata that was created.

This dashboard handles the CRUD functionalities of the Strategies, Groups, Datasets and MLModels.

The implementations that were being made during the last term are build on the already existing project. There is this [README.md](./README.md) and an additional [DEV-DOCUMENT.md](./DEV-DOCUMENT.md) for you to read to gain a better understanding of the code. For your future project work you should follow our lead and copy the current documents into the [./doc/archive](./doc/archive/) folder keeping the naming convention. You can then update it with your changes made. Also checkout the following table with information about the archived documents. When adding something to the archive it is mandatory to update the table.

| Semester   | Author                                     | Link to file                                            |
| ---------- | ------------------------------------------ | ------------------------------------------------------- |
| SS 2025    | Elisa Zhang, Martin Galacz & Ricardo Lauth | [README.md](./README.md)                                |
| SS 2025    | Elisa Zhang, Martin Galacz & Ricardo Lauth | [DEV-DOCUMENT.md](./DEV-DOCUMENT.md)                    |
| WS 2023/24 | Tim Smolne                                 | [README.md](./README.md)                                |
| WS 2023/24 | Tim Smolne                                 | [DEV-DOCUMENT.md](./DEV-DOCUMENT.md)                    |
| SS 2023    | Katharina Machilek & Tim Smolne            | [README.md](./doc/archive/2023SS-README.md)             |
| SS 2023    | Katharina Machilek & Tim Smolne            | [DEV-DOCUMENT.md](./doc/archive/2023SS-DEV-DOCUMENT.md) |
| WS 2022/23 | Katharina Machilek                         | [README.md](./doc/archive/2022WS-README.md)             |
| WS 2022/23 | Katharina Machilek                         | [DEV-DOCUMENT.md](./doc/archive/2022WS-DEV-DOCUMENT.md) |
| SS 2022    | Alexander Stumpf & Margad-Erdene Enkhee    | [README.md](./doc/archive/2022SS-README.md)             |
| SS 2022    | Alexander Stumpf & Margad-Erdene Enkhee    | [DEV-DOCUMENT.md](./doc/archive/2022SS-DEV-DOCUMENT.md) |

## Credentials

### 1. Dashboard Login

After setting up everything you can check out the dashboard under <http://localhost:3000>. If the connection to KeyCloak works properly, you should see a login form. Enter the following **credentials** to proceed.

-   Username: **admin**
-   Password: **admin**

### 2. KeyCloak Login

In some cases it might be necessary to log into the KeyCloak instance. This is necessary e.g. when you run into CORS errors (see [Troubleshooting](#troubleshooting)). The keycloak login can be found at <http://localhost:8080>.

-   Username: **keycloak**
-   Password: **keycloak**

## Setup

This repository contains the frontend implementation for the dashboard. It cannot run independently as it requires the API and services like KeyCloak to work properly. The easiest way to setup everything you need is to start the docker-compose environment implemented in the [Full Stack Repository](https://github.com/JsAntoPe/Data_Governance_Full_Stack). Follow its README.md to have the app running.

### Preparation

> From here on it is required to have the [docker-compose environment](https://github.com/JsAntoPe/Data_Governance_Full_Stack) up and running!

After setting up the docker-compose environment you need to stop the container for the dashboard to be able to make changes to it in an efficient way. You can either use the [Docker Desktop](https://www.docker.com/products/docker-desktop/) UI or the following command:

```sh
# make sure you are in the directory with the docker-compose.yml from the full-stack repository before running the command.
docker compose down web-dashboard
```

### Installing node.js packages

First we need to install the [node.js](https://nodejs.org/en) packages configured in the [package.json](./package.json). You can use [NPM](https://www.npmjs.com/) or [YARN](https://yarnpkg.com/) for that. Make sure your terminal is in the [./](./) directory before running one of the following commands.

```sh
# using npm
npm install
# using yarn
yarn install
```

If the installation fails, you can always add the **--force** flag to the command to ignore conflicts. This can be done during development as a quick fix but in the end you must ensure that all packages work together without having to force it.

The following packages are installed on top of the standard react packages. Update this list for any new package.

| Package           | Description                       |
| ----------------- | --------------------------------- |
| antd              | UI component library              |
| axios             | Tool for easy API access          |
| react-burger-menu | Burger menu for quick navigation. |
| react-helmet      | HTML head styling                 |
| react-router-dom  | React routing strategy            |
| json-diff-kit     | Comparing different JSON files    |
| lodash            | JavaScript utility library        |
| tailwindcss       | Utility-first CSS framework       |
| TanStack Query    | data-fetching library for react   |

### Starting the dashboard

If the installation went well you can now start the react application. The [package.json](./package.json) contains a script to help you with that.

```sh
# using npm
npm start
# using yarn
yarn start
```

Access the dashboard at <http://localhost:3000> after startup.

## Troubleshooting

When something is not working as expected, open the developer console in your browser (F12 in chrome) to check out the console log. Check if the error you are seeing has something in common with the following cases before asking google.

### CORS error

When running into a CORS error take the following steps to ensure that the KeyCloak client is configured correctly:

1. Login at <http://localhost:8080> (credentials are [here](#2-keycloak-login))
2. Switch the realm to _fml_ in the top left corner.
3. Click on _Clients_
4. Select _fml-webapp_ from the list (click on the name to access its details)
5. Scroll to _Web origins_ under _Access settings_
6. Make sure its content is a simple "+". If not, add it.
7. Don't forget to save your changes.

## Project Achievements SS2025

This semester, the project underwent a significant overhaul to improve stability, maintainability, and functionality.

-   **Full Codebase Modernization:** Migrated the entire frontend to a consistent, type-safe **TypeScript** stack.
-   **Architectural Refactoring:** Decomposed monolithic components into a modular, domain-driven structure, reducing the largest file from **>1700 to ~260 lines**.
-   **State Management Upgrade:** Implemented **Tanstack Query** for robust server state management, caching, and data-fetching.
-   **Deep Links:** Implemented Deep Linking.
-   **New Feature: Comparison View:** Added a dynamic view for side-by-side comparison of different versions of Datasets, Models, and Strategies.
-   **New Feature: Admin Dashboard:** Introduced a secure, role-based admin view for user and organization management.
-   **New Feature: Proposal Creation:** Added a functionality to write proposals.
-   **New Feature: Proposal Voting:** Added a functionality to vote on proposals and count them.
-   **New Feature: Result View:** Added a view to show results as diagrams (currently missing backend operations).

## Project Achievements WS2023/24

-   **Documentation**
    -   Updated the folder structure for the current and older versions of the README.md and dev-document.md. Before now, it was always a struggle to find the newest to get a reference when starting out with the project. Also added a Table with direct links to the old files in the main README. for quick access.
    -   Added a "Troubleshooting" section to the README.md with important information about common errors like CORS error with the REST-API.
    -   Fixed the HKA Logo at the README head as the image was no longer present in the repository.
-   **Dependencies**\n
    _Upgraded all npm dependencies of the web dashboard to their newest version._
    -   React
        -   Version 18.1 --> 18.2
        -   Moved the whole app to a new setup with TypeScript instead of JavaScript. Allows future groups to work with types for better code quality and hopefully less debugging.
    -   Ant Design
        -   Version 4.20.7 --> 5.15.1
        -   Reworked the main architecture of the app layout in consideration with the newest Ant components. This was necessary as the UI broke after the update. See more later under "Layout".
    -   KeyCloak
        -   Version 10.0.2 --> 24.0.1
        -   New KeyCloak Version in the backend required this as some unchangeable routes have changed.
    -   Axios
        -   Version 0.27.2 --> 1.6.7
        -   Getting rid of many vulnerabilities.
    -   Some other less relevant version changes.
-   **App Layout and appearance.**
    -   Because of how the upgrade from ant design v4 to v5 behaved i updated the app layout. I reworked the whole architecture in that context so that we now have some advanced implementation in that matter. To be more specific, the following advancements were made.
        -   The username is now displayed in the header with the ability to logout via a dropdown menu. Before, you could logout in the sidebar.
        -   The sidebar now has icons for each link and a new grouped section for the editable master data (datasets, strategies, ml models and groups).
        -   The navigation using the sidebar now works with the react router instead of HTML href attributes. This allows us to have routing without page reloads which makes the UX much smoother.
        -   I designed and added a Logo to the Header and Favicon. I used the brain-icon from <https://fontawesome.com> and changed some things so that it looks nice and fits to the apps' theme.
        -   The content section of the app got polished. Many buttons were realigned, and the page title now uses the same layout on every page for a seamless experience. All forms tables now use more space allowing the usage of the app on non-1080p screens.
-   **Datasets**
    -   Added the ability to import .json files when creating a new dataset. The form will be auto-filled. Errors in the .json format are detected and responded with an error message. Invalid or missing values result in a non-submittable form due to how the backend is implemented.
    -   To be able to fix incomplete data, especially in the dataset features, i added the option to edit a dataset feature within the "add dataset" form.
