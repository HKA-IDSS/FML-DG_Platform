<!-- PROJECT LOGO -->
<br />
<div align="center">
    <a href="https://www.h-ka.de/">
        <img src="../img/hka_logo.jpg" alt="Logo" width="40%">
    </a>
    <h1 align="center">Web-Dashboard for Data Governance of Federated ML</h1>
    <p align="center">
        <h3>Winterterm 2022/2023</h3>
        <br />
        Developed by Katharina Machilek
        <br />
        Supervised by José Antonio Peregrina Pérez & Prof. Dr. rer. nat. Christian Zirpins 
    </p>
</div>
<br />

<!-- ABOUT THE PROJECT -->
## About The Project

This project was created in order to support the users in conducting a successful FML training by helping with the 
definition of governance elements, agreeing upon them and analyzing the metadata that was created.

This dashboard handles the CRUD functionalities of the Strategies, Groups, Datasets and MLModels.

The implementations that were being made during the winterterm 2022/2023 build on an already existing project. The old 
readme file and documentation can be found here: [old readme.md](AlexanderREADME.md) and [old devdocument](src/doc/devdocument.md)

Please have a look at the developer document [dev-document](src/doc/dev-document.md) located inside the doc folder to 
gain a better understanding of the code.


<!-- SETUP -->
## Setup
The dashboard must be configured as follows in order to work properly. This section solely focuses on the setup of the 
dashboard and not on the setup of the API and backend.

As of lately the connection between the backend and the frontend was established. For the project to work properly 
please also set up the Api (https://iz-gitlab-01.hs-karlsruhe.de/klfa1015/data-governance-api-rest).
For the setup please follow the instructions in the README.md files of the corresponding repository.
After setting everything up you should be able to create and delete new strategies, datasets, ml-models and groups. 
Additionally, the dashboard is being managed with the help of Keycloak, so that the user is required to log in and so 
that the visibility of the content on the dashboard is restricted.
For logging in with keycloak, the user 'user' with the passwort 'user' was created.

### Requirements

You need to install one of two package managers.

* [NPM](https://www.npmjs.com/)

* [YARN](https://yarnpkg.com/)



### Installation and configuration

1. First, run a command in the top-level directory to install all packages/node modules via package manager.
```sh
$ npm install
```
or

```sh
$ yarn install
```

2. In case the install doesn't work correctly due to dependency conflicts, simply rerun the last command with the --force flag.

```sh
$ npm install --force
```

```sh
$ yarn install --force
```

### NPM Modules

Automatically installed by the last step(s).
```sh
$ npm install
```

```sh
$ yarn install
```
NPM packages:

* [antd](https://www.npmjs.com/package/antd)
* [axios](https://www.npmjs.com/package/axios)
* [react-burger-menu](https://www.npmjs.com/package/react-burger-menu)
* [react-helmet](https://www.npmjs.com/package/react-helmet)
* [react-router-dom](https://www.npmjs.com/package/react-router-dom)
* [json-diff-kit](https://www.npmjs.com/package/json-diff-kit)

YARN packages:

* [antd](https://yarnpkg.com/package/antd)
* [axios](https://yarnpkg.com/package/axios)
* [react-burger-menu](https://yarnpkg.com/package/react-burger-menu)
* [react-helmet](https://yarnpkg.com/package/react-helmet)
* [react-router-dom](https://yarnpkg.com/package/react-router-dom)
* [json-diff-kit](https://yarnpkg.com/package/json-diff-kit)

antd is a great UI component library     
axios is a tool for an easier API creation    
react-burger-menu takes care of the burger menu. It might produce a dependency conflict, which is handled by the --force flag at npm install    
react-helmet sets the general page color for all components    
react-router-dom takes care of react routing     
json-diff-kit compares different json files

<!-- USAGE -->

### Usage - start the dashboard

To start the dashboard, execute this command.
```sh
$ npm start
```

```sh
$ yarn start
```

in the top directory (in fmldatagncdashboard).

After that the dashboard should soon be accessible under [localhost](http://localhost:3000/). It runs on Port 3000 by default.

<!-- Code Documentation -->
## Code documentation

The more detailed explanation of the code is located in the [dev-document](src/doc/dev-document.md) markdown file in the doc folder.
