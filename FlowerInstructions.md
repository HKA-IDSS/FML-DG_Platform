# Flower Instructions.

Most of the instructions for running flower has been summarized in the following places:
- src/fl-training-experiments/Preprocessing Notebook.
- src/fl-training-experiments/Client.py

The first serves to modify the dataset to make it consistent with those of the other participants.

The second serves to run the training process. It requires as inputs the number of columns of the newly created dataset, as well as the dimensions of the model.

To run the client, first ask the organizer to activate the server. Then, run in the FLTrainingExperimentsClient(number) folder:

```poetry run python src\fl-training-experiments\Client.py```