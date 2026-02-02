# A platform for Federated Machine Learning Data Governance (FML-DG).

### Instrucciones

This is the platform implementing the application of Data Governance to Federated Learning, following the research presented in the paper *Towards Data Governance for Federated Machine Learning* (link: https://link.springer.com/chapter/10.1007/978-3-031-23298-5_5).

To use the platform, we recommend following the steps outlined below (**bold** content below represents the actual entities that users of this platform can create):

1. First, create a **Group**. The **Group** entity comprises members who wish to perform FL training together.

* Let one of the members of the group create the **Strategy**. The **Strategy** represents a first description of the goal being pursued.

* From the **Strategy**, it is recommended that users start by proposing **Quality Requirements**. To do this, go to the **Strategy** of interest, and click **Proposals**. There, you can propose either **Quality Requirements** or **Configurations** (the latter needs **ML Models** and **Datasets**).

 * Before continuing with the creation of other artifacts, it needs to be reminded that both **Quality Requirements** and **Configurations** are *proposed*, not *created*. This means that each proposal needs to be approved by other members, which is done by voting. **Quality Requirements** are approved by a yes/no vote individually. **Configurations** are approved by majority voting over the set of existing proposals.

* For the **ML Models**, users can use the default models available right now (MLP and XGBoost), or modify the hyperparameters to their preference. The rest of the models are currently not available.

* The **Datasets** are the most interesting part of the platform. Here, the users can propose dataset structures that other users can aim to match for the FL training. The **Dataset** contains the following information:
 * Name: Name of the column.
 * Description: Description of the column (informative)
 * Type of value: Whether the value is a number (integer, float, etc), a boolean, or a string.
 * Valid values: Depends on the type of value. 
   * If numeric, the valid values are two: the Minimum and Maximum values.
   * If string, the valid values are a list of N categories.
   * If boolean, no valid values needed.
 * Group: Not available.
 * Preprocessing: Multiple types, depending on the data:
   * Min_max_encoder: For numeric, it uses the minimum and maximum values for scaling the data.
   * Standard_encoder: Not available.
   * Label encoder: It transforms all categories into integer numbers, following the order defined in the list.
   * One_hot_encoder: It generates a column per category, and it sets a one in the column matching the value of the category.

* For the last part, once everything else is defined, participants can now define **Training Configurations**. For this, the user can go to **Strategies** -> The strategy of interest -> **Proposals** -> Create the **Training Configuration** selecting the **ML Models**, the **Datasets**, and their versions.
* Once the training configurations are proposed, they can be voted on based on preference.

When one training configuration is accepted, the user needs to pass to the secondary interface, in the FLClient repository, or folder. There, he needs to follow these steps:

1. In the folder FLClient run 

```poetry run python src\fl-client\main.py```

2. Check the possible training rounds clicking **1**.

3. Copy the hash of the training rounds in which you wish to participate. Keep it copied.

4. Click **2** to register a dataset. First paste the hash of the training, then write the name of the dataset (including the .csv).

5. If there is an error in the dataset, it will mention it, and you can check the report printed in the tmp folder. Correct the errors in the preprocessing notebook, and return to 1.

6. If there are no error, the dataset will be registered. Now, to participate in the training, simply click **3** and paste again the hash of the training.

This should run the training until the end. In the logs, you can consult the results.

