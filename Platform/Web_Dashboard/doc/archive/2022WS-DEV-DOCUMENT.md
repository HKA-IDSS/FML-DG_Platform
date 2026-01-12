<!-- Foreword -->
# Foreword

This project is written in Javascript and uses react. The structure of the JS Code is mainly done with functional components. This documentation expects basic react knowledge about the xml like structure. Furthermore knowledge about the used various modules helps a lot.

## src/index.js

The root of this project is the index.js in the src folder. The <App> component is rendered here.

## src/App.js

The strucutre of the project lies here, what should be rendered. Furthermore the routing is also solved in this file. Routing tells the program to render a specific component at a certain path.     
The Sidebar component is imported as the burger.    
React-Helmet is imported to set the general background color for all components below.

## src/components/Sidebar.jsx

This is the Burger Menu, it offers several opportunites. If a link is clicked, the component changes as defined by the routing.

## src/components/index.jsx

To avoid lots of import in other files, this file can take care of it. Just import all components in this index.jsx, and import the needed component in the needed page via "from './components'". Like in the App.js, "import { Sidebar } from './components';".

## src/api/index.js

Connects to the backend. Imports the module axios, which is used for an easier API creation. Calls the different functions of the backend at the defined path with defined payloads or without any. Watch out that some Backend functions expects the payload in the link and not as a body. This api exports all functions and makes them accesible to the other components. As long as the Possibility of keeping the current group stored per user profile is not given, the current group is a set variable when needed in the api calls.

## src/pages/index.js

Works as equal as src/components/index.jsx.

## src/components/MLModelsFunctional.jsx

Display all MLModels and offers the opportunity to create new as well as Delete existing. Offers the functionality to expand the description of an MLModel. The main structure of the code is solved by Modals (https://ant.design/components/modal/). In the Code the Modals are structured above each other, the visiblity of those modals are changed by the modals internally. Modals are used for Comparison Functionality as well. You can select 2 different rows of table at the same time and then you can compare and see difference between them. (see details in explanation of the comparison functionality)

## src/components/GroupsFunctional.jsx

Display all Groups and offers the opportunity to create new as well as Delete existing. The main structure of the code is solved by Modals (https://ant.design/components/modal/). In the Code the Modals are structured above each other, the visiblity of those modals are changed by the modals internally. 

## src/components/DatasetsFunctional.jsx

Display all Datasets and offers the opportunity to create new as well as Delete existing. Offers the functionality to expand the features of the dataset, for this we need another columns definition. const expandedRow receives the current row, and renders the subtable. The main structure of the code is solved by Modals (https://ant.design/components/modal/). In the Code the Modals are structured above each other, the visiblity of those modals are changed by the modals internally. Modals are used for Comparison Functionality as well. You can select 2 different rows of table at the same time and then you can compare and see difference between them. (see details in explanation of the comparison functionality)

## src/components/StrategiesFunctional.jsx

Display all Strategies and offers the opportunity to create new as well as Delete existing. It has several columns because the first modal offers to check the Quality Requirements as well as the training configurations. Unfortunately there are lots of Modals in this Component, but because the stratgies offer lots of functionalities this is necessary.     
Modal1 offers an edit Strategy Screen.
Modal2 offers to add another Strategy.
Modal3 offers to have a look at the Quality Requirements.
Modal4 offers to edit the training configs.
Modal5 offers to create another training config.
Modal6 displays an specific Quality Requirement as an JSON.
Modal2Compare displays difference between compared items and JSON.
The main structure of the code is solved by Modals (https://ant.design/components/modal/). In the Code the Modals are structured above each other, the visiblity of those modals are changed by the modals internally. Modals are used for Comparison Functionality as well. You can select 2 different rows of table at the same time and then you can compare and see difference between them. (see details in explanation of the comparison functionality)

## Brief explanation of the comparison functionality 

Basically, to compare 2 JSONs, both JSONs have to be sorted first. To do this, used "merge sort" by adding empty lines. The result would look like this: 
```
[start]                                |   [result]
        p: ↓                           |          p:                               ↓
 keysLeft: a  d  f  g  i  j  k  l      |   keysLeft: a  _  _  d  f  g  i  j  k  l
keysRight: a  b  c  d  i               |  keysRight: a  b  c  d  _  _  i  _  _  _
        q: ↑                           |          q:                               ↑
```
Then we have 2 arrays, **left** and **right**:

1. Let **p** and **q** point to **left[0]** and **right[0]**.
2. If there is no more value in **left**, output "the rest of **right** is added"; if there is no more value in **right**, output "the rest of **left** is added".
3. If **p** and **q** are different:

- If **p** and **q** are both arrays, differentiate them recursively;
- Else, output "**p** is modified to **q**".
4. Else, output "equal".

The diff results may include  type: *'modify' | 'add' | 'remove' | 'equal'*, text: *string* and lineNumber: *number*.

