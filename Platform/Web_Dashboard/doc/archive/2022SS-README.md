<!-- PROJECT LOGO -->
<br />
<div align="center">
    <a href="https://www.h-ka.de/">
        <img src="../img/hka_logo.jpg" alt="Logo" width="40%">
    </a>
    <h1 align="center">Web-Dashboard for Data Governance of Federated ML</h1>
    <p align="center">
        <h3>Project 1 and 2, Summerterm 2022</h3>
        <br />
        Developed by Alexander Stumpf and by Margad-Erdene Enkhee
        <br />
        Supervised by José Antonio Peregrina Pérez & Prof. Dr. rer. nat. Christian Zirpins 
    </p>
</div>
<br />

<!-- ABOUT THE PROJECT -->
## About The Project
For the Federated Machine Learning at the HKA, a Communication between the participants of the projects is necessary and such a dasboard would simplify this process of communication.    

This dashboard handles the CRUD functionalities of the Strategies, Groups, Datasets and MLModels.

This project 2 means that it is based on implementation of project 1 and extended with comparison functionality.

This whole project can be extended with new features like the ability to log in, maintain user profiles, and control the group ids that are kept in those profiles.

Please have a look at the developer document located inside the doc folder to gain a better understanding of the Code.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- SETUP -->
## Setup

The following setup is required to run the dashboard properly. This Setup expects that everything regarding the API & Backend is already correctly setup and reachable under 127.0.0.1:5000.
     
Furthermore there has been a change to get the Dashboard and the Backend connected, the Python Server did get the tool flask-cors installed. The code did change in 2 lines as followed:    

At the server.py
```
[...]
from flask_cors import CORS # New due to flask-cors

[...]

    def __create_app(self, db):
        app = Flask(__name__, instance_relative_config=True)
        api = Api(app)
        CORS(app, resources={"*": {"origins": "*"}}) # New due to flask-cors

        api.add_resource(Groups, '/groups', '/groups/<string:group_id>',
                         resource_class_kwargs={'db': db})

[...] 
```

Without this tool there are no requests between frontend and backend possible.

### Requirements

You need to install one of varios package managers.

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

Automatically installed by the last step(s)
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
axios is an tool for an easier API creation    
react-burger-menu takes care of the burger menu. It might produce a dependency conflict, which is handled by the --force flag at npm install    
react-helmet sets an general page color for all components    
react-router-dom takes care of react routing     
json-diff-kit compares json files

<p align="right">(<a href="#top">back to top</a>)</p>
<!-- USAGE -->

### Usage - start the dashboard

To start the dashboard, execute this command.
```sh
$ npm start
```

```sh
$ yarn start
```

in the top directory.

After that the dashboard should soon be accessible under [localhost](http://localhost:3000/). It runs on Port 3000 by default.

<!-- Code Documentation -->
## Code documentation

The more detailed explanation of the code locates in the [devdocument](src/doc/devdocument.md) markdown file in the doc folder.

<p align="right">(<a href="#top">back to top</a>)</p>
