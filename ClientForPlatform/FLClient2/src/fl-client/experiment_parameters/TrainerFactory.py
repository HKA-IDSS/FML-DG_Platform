from abc import ABC, abstractmethod
from typing import Type, List, Tuple

from flwr.client import NumPyClient
from flwr.server.strategy import Strategy
from pandas import DataFrame

from experiment_parameters.model_builder.Model import Model
from experiment_parameters.model_builder.ModelBuilder import Director
from experiment_parameters.strategies.client.FedAvgClient import FedAvgClient
from experiment_parameters.strategies.client.FedAvgEmbeddingClient import FedAvgClientEmbedding
# from experiment_parameters.strategies.client.FedGKDClient import FedGKDClient
# from experiment_parameters.strategies.client.FedLFClient import FedLFClient
# from experiment_parameters.strategies.client.FedDGKDClient import FedDGKDClient
from experiment_parameters.strategies.client.FedXGBoostClient import FedXGBoostClient
from experiment_parameters.strategies.server.FedAvgRewritten import FedAvgRewritten
# from experiment_parameters.strategies.server.FedKD import FedKD
# from experiment_parameters.strategies.server.FedGKD import FedGKD
# from experiment_parameters.strategies.server.FedLF import FedLF
# from experiment_parameters.strategies.server.FedDGKD import FedDGKD
# from experiment_parameters.strategies.server.FedDKD import FedDKD
from experiment_parameters.strategies.server.FedXgbBagging import FedXgbBagging

"""
Two Abstract Factories in this file:
    1. Factory for Strategy-Client
    2. Factory for Dataset-Model

First strategies and their corresponding code on client.

Second, factories for retrieving the dataset and the models with
parametrized for such datasets.
"""


class AbstractFactoryStrategyClient(ABC):
    @abstractmethod
    def create_strategy(self) -> Type[Strategy]:
        pass

    @abstractmethod
    def create_client(self) -> Type[NumPyClient]:
        pass


class ConcreteFactoryFedAvg(AbstractFactoryStrategyClient):

    def create_strategy(self) -> Type[Strategy]:
        return FedAvgRewritten

    def create_client(self) -> Type[NumPyClient]:
        return FedAvgClient

#
# class ConcreteFactoryCentralizedKD(AbstractFactoryStrategyClient):
#
#     def create_strategy(self) -> Type[Strategy]:
#         return FedKD
#
#     def create_client(self) -> Type[NumPyClient]:
#         return FedAvgClient


class ConcreteFactoryXGBoostBagging(AbstractFactoryStrategyClient):

    def create_strategy(self) -> Type[Strategy]:
        return FedXgbBagging

    def create_client(self) -> Type[NumPyClient]:
        return FedXGBoostClient

#
# class ConcreteFactoryLocalKnowledgeFusion(AbstractFactoryStrategyClient):
#
#     def create_strategy(self) -> Type[Strategy]:
#         return FedLF
#
#     def create_client(self) -> Type[NumPyClient]:
#         return FedLFClient
#
#
# class ConcreteFactoryGlobalKD(AbstractFactoryStrategyClient):
#
#     def create_strategy(self) -> Type[Strategy]:
#         return FedGKD
#
#     def create_client(self) -> Type[NumPyClient]:
#         return FedGKDClient
#
#
# class ConcreteFactoryDecoupledGKD(AbstractFactoryStrategyClient):
#
#     def create_strategy(self) -> Type[Strategy]:
#         return FedDGKD
#
#     def create_client(self) -> Type[NumPyClient]:
#         return FedDGKDClient
#
#
# class ConcreteFactoryDecoupledKD(AbstractFactoryStrategyClient):
#
#     def create_strategy(self) -> Type[Strategy]:
#         return FedDKD
#
#     def create_client(self) -> Type[NumPyClient]:
#         return FedAvgClient

#
# class AbstractFactoryModelPerDataset(ABC):
#     """
#     In this abstract factory, you need to update whenever you add a new type of model.
#     """
#     _dataset: Dataset
#
#     def get_dataset(self) -> Dataset:
#         return self._dataset
#
#     @abstractmethod
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         """
#         At the moment, make this return a null. It is not required to use synthetic data.
#         """
#         pass
#
#     @abstractmethod
#     def get_mlp(self, logits: bool) -> Model:
#         pass
#
#     @abstractmethod
#     def get_tabnet(self, logits: bool) -> Model:
#         pass
#
#     def get_input_dimensions(self):
#         return self._dataset.x_test.shape[1]
#
#     def get_output_dimensions(self):
#         return self._dataset.y_test.shape[1]
#
#
# class ConcreteFactoryDatasetWine(AbstractFactoryModelPerDataset):
#
#     def __init__(self):
#         self._dataset = WineDataset()
#
#     def get_synthetic_dataset(self) -> Dataset:  # Tuple[DataFrame, DataFrame]:
#         return WineDataset()
#
#     def get_mlp(self, logits: bool = False) -> Model:
#         if logits:
#             return NeuralNetworkWineLogits()
#         else:
#             return NeuralNetworkWine()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetWine()
#
#
# class ConcreteFactoryDatasetIris(AbstractFactoryModelPerDataset):
#
#     def __init__(self):
#         self._dataset = IrisDataset()
#
#     def get_synthetic_dataset(self) -> Dataset:  # Tuple[DataFrame, DataFrame]:
#         return IrisDataset()
#
#     def get_mlp(self, logits: bool) -> Model:
#         if logits:
#             return NeuralNetworkIrisLogits()
#         else:
#             return NeuralNetworkIris()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetIris()
#
#
# class ConcreteFactoryDatasetHumanActivityRecognition(AbstractFactoryModelPerDataset):
#     def __init__(self):
#         self._dataset = HumanActivityRecognitionDataset()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         return MLPHumanActivityRecognition()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetHumanActivityRecognition()
#
#
# class ConcreteFactoryDatasetAdult(AbstractFactoryModelPerDataset):
#     def __init__(self):
#         self._dataset = AdultDataset()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         return MLPAdult()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetAdult()
#
#
# class ConcreteFactoryDatasetCovertype(AbstractFactoryModelPerDataset):
#     def __init__(self):
#         self._dataset = CovertypeDataset()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         return MLPCoverType()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetCoverType()
#
#
# class ConcreteFactoryDatasetHeart(AbstractFactoryModelPerDataset):
#
#     def __init__(self):
#         self._dataset = HeartDataset()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         pass
#
#     def get_tabnet(self, logits: bool) -> Model:
#         pass
#
#
# class ConcreteFactoryDatasetBinaryHeart(AbstractFactoryModelPerDataset):
#
#     def __init__(self):
#         self._dataset = HeartDatasetBinary()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         return MLPHeartBinary()
#
#     def get_tabnet(self, logits: bool) -> Model:
#         return TabNetHeartBinary()
#
#
# class ConcreteFactoryDatasetNewAdult(AbstractFactoryModelPerDataset):
#
#     def __init__(self):
#         self._dataset = NewAdultDataset()
#
#     def get_synthetic_dataset(self) -> Tuple[DataFrame, DataFrame]:
#         pass
#
#     def get_mlp(self, logits: bool) -> Model:
#         pass
#
#     def get_tabnet(self, logits: bool) -> Model:
#         pass
#
#
# class ModelBuilder(ABC):
#
#     @abstractmethod
#     def set_input(self):
#         pass
#
#     @abstractmethod
#     def create_mlp(self, input_dim: int, neurons_and_activation_function_layer: List[Tuple[int, str]], output_dim: int):
#         pass
#
#     @abstractmethod
#     def create_tabnet(self, input_dim: int, output_dim: int):
#         pass
#
#     @abstractmethod
#     def define_compiler(self):
#         pass
#
#
# class ModelBuilderSoftmax(ModelBuilder):
#
#     @abstractmethod
#     def set_input(self):
#         pass
#
#     @abstractmethod
#     def create_mlp(self, input_dim: int, neurons_and_activation_function_layer: List[Tuple[int, str]], output_dim: int):
#         pass
#
#     @abstractmethod
#     def create_tabnet(self, input_dim, output_dim):
#         pass
#
#     @abstractmethod
#     def define_compiler(self):
#         pass
#
#
# class ModelBuilderLogits(ModelBuilder):
#     """
#     Unused class, because at the moment, I am not thinking on adding parametrization for models
#     from the arguments parsing.
#     """
#
#     @abstractmethod
#     def set_input(self):
#         pass
#
#     @abstractmethod
#     def create_mlp(self, input_dim: int, neurons_and_activation_function_layer: List[Tuple[int, str]], output_dim: int):
#         pass
#
#     @abstractmethod
#     def create_tabnet(self, input_dim, output_dim):
#         pass
#
#     @abstractmethod
#     def define_compiler(self):
#         pass


# class Director:
#     builder: ModelBuilder
#
#     def __init__(self, builder):
#         self.builder = builder
#
#     def builder(self) -> ModelBuilder:
#         return self.builder
#
#     def build_mpl(self):
#         self.builder.initialize_data()
#         self.builder.initialize_model()
#         self.builder.initialize_strategy()
#         self.builder.initialize_client()


########## Export Dictionaries ##########

"""Add here instances of new concrete Factories."""

strategies_dictionary = {
    "FedAvg": ConcreteFactoryFedAvg(),
    # "FedKD": ConcreteFactoryCentralizedKD(),
    # "FedLF": ConcreteFactoryLocalKnowledgeFusion(),
    # "FedGKD": ConcreteFactoryGlobalKD(),
    # "FedDKD": ConcreteFactoryDecoupledKD(),
    # "FedDGKD": ConcreteFactoryDecoupledGKD(),
    "FedXGB": ConcreteFactoryXGBoostBagging(),
    "FedMobileB2C": FedAvgClientEmbedding
}

# dataset_model_dictionary = {
#     "wine": ConcreteFactoryDatasetWine(),
#     # "iris": ConcreteFactoryDatasetIris(),
#     "har": ConcreteFactoryDatasetHumanActivityRecognition(),
#     "adult": ConcreteFactoryDatasetAdult(),
#     "covertype": ConcreteFactoryDatasetCovertype(),
#     "heart": ConcreteFactoryDatasetHeart(),
#     "binary_heart": ConcreteFactoryDatasetBinaryHeart(),
#     "new_adult": ConcreteFactoryDatasetNewAdult()
# }


def factory_return_model(input_dim, output_dim, model_type: str, parameters) -> Model:
    """
    Function to add the models corresponding to the different datasets.
    """
    director = Director()
    if model_type == "mlp":
        # input_parameters = factory.get_input_dimensions()
        # input_parameters = 104
        # num_classes = factory.get_output_dimensions()
        return director.create_mlp(input_dim, output_dim, parameters)

    elif model_type == "xgboost":
    #     input_parameters = factory.get_input_dimensions()
    #     num_classes = factory.get_output_dimensions()
        return director.create_xgboost(input_dim, output_dim, parameters)
