<!-- Foreword -->
# Foreword

This project is written in Javascript and uses react. The structure of the JS Code is mainly done with functional components. This documentation expects basic react knowledge about the xml like structure.
Furthermore, knowledge about the used various modules helps a lot.

## src/index.js

The root of this project is the index.js in the src folder. The `<App>` component is rendered here.

## src/App.js

The structure of the project lies here, what should be rendered. Furthermore, the routing is also solved in this file.
Routing tells the program to render a specific component at a certain path.  
The Sidebar component is imported as the burger.
React-Helmet is imported to set the general background color for all components below.
Keycloak is included in the application by including the 'ReactKeycloakProvider'. Additionally, in every Route, a
PrivateRoute is added. This PrivateRoute checks, if the user is logged in and authorized to see the corresponding page.

## src/keycloak.js

A new keycloak client instance is created here and used in App.js.

## src/components/Sidebar.jsx

This is the Burger Menu, it offers several opportunities. If a link is clicked, the component changes as defined by the 
routing.

## src/components/index.jsx

To avoid lots of import in other files, this file can take care of it. Just import all components in this index.jsx, 
and import the needed component in the needed page via "from './components'". Like in the App.js, "import { Sidebar } 
from './components';".

## src/api/index.js

Connects to the backend. Imports the module axios, which is used for an easier API creation. Calls the different 
functions of the backend at the defined path with defined payloads or without any. Watch out that some Backend functions 
expects the payload in the link and not as a body. This api exports all functions and makes them accessible to the other 
components. With every api-call the keycloak token needs to be extracted and put into the call.

## src/pages/index.js

Works as equal as src/components/index.jsx.

## src/pages/MLModelsFunctional.jsx

Display all MLModels and offers the opportunity to create new as well as Delete existing. Offers the functionality to 
expand the description of an MLModel. 

## src/pages/GroupsFunctional.jsx

Display all Groups and offers the opportunity to create new as well as Delete existing. Additionally, groups can be
shown and edited.

## src/pages/DatasetsFunctional.jsx

Display all Datasets and offers the opportunity to create new as well as Delete existing. 

## src/pages/StrategiesFunctional.jsx

Display all Strategies and offers the opportunity to create new as well as Delete existing.

## src/pages/Users.jsx

Display the current user and the groups the user is assigned to.

## src/components/datasetFeatureModalForm.jsx

Displays a modal that contains a form for a dataset feature.

## src/components/tagInput.jsx

Contains a tag input field that can be used by any form as an additional input field.

<details><summary>Example</summary>

```js
<TagInput
        initialValue={editAttributeFormValues.sub_features}
        valueChange={(val) =>
        editAttributeForm.setFieldValue('sub_features', val)
        }
        textNew='Add Attribute'
        textNone='No attributes'
/>
```

</details>

## Brief explanation of the comparison functionality

The comparison functionality is used in the strategy-, dataset- and ml-model-section. Basically, to compare 2 JSONs, 
both JSONs have to be sorted first. To do this, used "merge sort" by adding empty lines.
The result would look like this:

```txt
[start]                                |   [result]
        p: ↓                           |          p:                               ↓
 keysLeft: a  d  f  g  i  j  k  l      |   keysLeft: a  _  _  d  f  g  i  j  k  l
keysRight: a  b  c  d  i               |  keysRight: a  b  c  d  _  _  i  _  _  _
        q: ↑                           |          q:                               ↑
```

Then we have 2 arrays, **left** and **right**:

1. Let **p** and **q** point to **left[0]** and **right[0]**.
2. If there is no more value in **left**, output "the rest of **right** is added"; if there is no more value in
   **right**, output "the rest of **left** is added".
3. If **p** and **q** are different:
        - If **p** and **q** are both arrays, differentiate them recursively;
        - Else, output "**p** is modified to **q**".
4. Else, output "equal".

The diff results may include  type: *'modify' | 'add' | 'remove' | 'equal'*, text: *string* and lineNumber: *number*.

## Future work

in the future the possibility:

- Edit ml-model, dataset and groups
- Give rights to group and it's users
- Generate result from the training configurations
- Combine the two backend branches so that keycloak works with - the voting process
- Implementation of the voting process
