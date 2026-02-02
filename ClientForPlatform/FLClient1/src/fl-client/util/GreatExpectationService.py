import typing

from great_expectations import expectations as gxe
import great_expectations as gx
from great_expectations.validator.validator import Validator
from great_expectations.core.batch import RuntimeBatchRequest


class GreatExpectationService:
    GENERAL_TO_PANDAS = {
        "integer": ["int64", "Int64", "int32", "Int32"],
        "float": ["float64", "float32"],
        "string": ["object", "StringDtype", "string", "category", "str"],
        "boolean": ["bool", "boolean"],
        "datetime": ["datetime64[ns]", "datetime64"],
    }

    def __init__(self):
        self.context = gx.get_context()
        self.data_source = self.context.data_sources.add_pandas(name="pandas_source")
        self.data_asset = self.data_source.add_dataframe_asset(name="pandas_asset")
        self.batch_definition = self.data_asset.add_batch_definition_whole_dataframe(
            "pandas_batch"
        )

        suite = gx.ExpectationSuite(name="Data Validation Expectations")
        self.suite = self.context.suites.add(suite)

    def add_expectations_from_configuration(self, validation_configuration):
        dataset_features = validation_configuration.get("dataset_features", [])
        column_mappings = validation_configuration.get("column_mappings", {})

        if dataset_features:
            for expectation in dataset_features:
                if expectation.get('type'):
                    self.add_type_expectation(expectation['name'], expectation['type'])
                if "valid_values" in expectation:
                    self.add_values_expectation(expectation['name'], expectation['valid_values'])
                if "range" in expectation:
                    self.add_range_expectation(expectation['name'], expectation['range'])
                if "one_hot" in expectation and expectation["one_hot"] is True:
                    self.add_one_hot_expectations(expectation["name"], expectation["sub_features"])
                if "regex" in expectation:
                    self.add_regex_expectation(expectation["name"], expectation["regex"])
        if column_mappings:
            for mapping in column_mappings:
                self.add_mapping_validation(mapping['mappings'], mapping['column_a'], mapping['column_b'])

    def add_mapping_validation(self, mappings, column_a, column_b):
        self.suite.add_expectation(
            gx.expectations.ExpectColumnPairValuesToBeInSet(
                column_A=column_a,
                column_B=column_b,
                value_pairs_set=[(key, value) for key, value in mappings.items()]
            )
        )
        print(f"Added mapping validation for {column_a} -> {column_b} with mapping {mappings}")

    def add_regex_expectation(self, name, regex):
        if not regex:
            raise ValueError("The regex pattern cannot be empty.")

        self.suite.add_expectation(
            gx.expectations.ExpectColumnValuesToMatchRegex(
                column=name,
                regex=regex
            )
        )
        print(f"Added regex expectation for {name} with pattern: {regex}")

    def add_type_expectation(self, name, type):
        print(f"Adding type expectation for {name} with type: {type}")
        pandas_types = self.GENERAL_TO_PANDAS.get(type, [])
        if not pandas_types:
            raise ValueError(
                f"Unknown general type '{type}'. Supported types are: {list(self.GENERAL_TO_PANDAS.keys())}")
        self.suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInTypeList(
                column=name,
                type_list=pandas_types
                # result_format={
                #     "result_format": "COMPLETE",
                #     "unexpected_index_column_names": ["all_indexes"],
                #     "return_unexpected_index_query": True,
                # }
            )
        )

    def add_values_expectation(self, name, valid_values):
        if not valid_values:
            raise ValueError("The valid_values list cannot be empty.")

        if all(isinstance(val, bool) for val in valid_values):
            self.suite.add_expectation(
                gx.expectations.ExpectColumnValuesToBeInSet(
                    column=name,
                    value_set=[True, False],
                    mostly=1
                    # result_format={
                    #     "result_format": "COMPLETE",
                    #     "unexpected_index_column_names": ["all_indexes"],
                    #     "return_unexpected_index_query": True,
                    # }
                )
            )
            print(f"Added boolean expectation for {name} with valid values: {valid_values}")
        else:
            self.suite.add_expectation(
                gx.expectations.ExpectColumnValuesToBeInSet(
                    column=name,
                    value_set=valid_values,
                    mostly=1
                    # result_format={
                    #     "result_format": "COMPLETE",
                    #     "unexpected_index_column_names": ["all_indexes"],
                    #     "return_unexpected_index_query": True,
                    # }
                )
            )
            print(f"Added set expectation for {name} with valid values: {valid_values}")

    def add_range_expectation(self, name, range):
        min_value, max_value = sorted(range)
        self.suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column=name,
                min_value=min_value,
                max_value=max_value,
                mostly=1
                # result_format={
                #     "result_format": "COMPLETE",
                #     "unexpected_index_column_names": ["all_indexes"],
                #     "return_unexpected_index_query": True,
                # }
            )
        )
        print(f"Added range expectation for {name}: {min_value} to {max_value}")

    def add_one_hot_expectations(self, name, sub_features):
        print(f"Adding one hot constraints for for {name}...")

        if not sub_features or not isinstance(sub_features, list):
            raise ValueError(f"Invalid sub_features list for {name}")

        self.suite.add_expectation(
            gx.expectations.ExpectMulticolumnSumToEqual(
                column_list=sub_features,
                sum_total=1.,
                mostly=1
                # result_format={
                #     "result_format": "COMPLETE",
                #     "unexpected_index_column_names": ["all_indexes"],
                #     "return_unexpected_index_query": True,
                # }
            )
        )
        print(f"Added one hot column sum constraint for {name}")

    def run_validation_on_pandas(self, pd):
        batch_parameters = {"dataframe": pd}
        batch = self.batch_definition.get_batch(batch_parameters=batch_parameters)
        # complete_result_format_dict = {"result_format": "COMPLETE"}

        validation_definition = gx.ValidationDefinition(
            data=self.batch_definition, suite=self.suite, name="pandas_definition"
        )
        return validation_definition.run(batch_parameters=batch_parameters, result_format="COMPLETE")
