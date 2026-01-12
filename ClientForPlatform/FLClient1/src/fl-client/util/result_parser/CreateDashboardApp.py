from dash import dash, Dash, dcc, html, Input, Output
from util.result_parser.CreateFigures import determine_and_create_fig

def create_and_run_app(directory_dict, all_display_options, all_results, dataframes_per_result):
    # Initialization
    app = dash.Dash()

    # Style app layout with dash components
    app.layout = html.Div(
        [
            html.Div(
                [
                    # These are the dropdowns for the first graph
                    html.Div(
                        [
                            html.H3("Configuration for Graph 1:"),
                            html.Label(["Dataset:"], style={"paddingTop": "8px"}),
                            dcc.Dropdown(
                                id="dataset-picker-1",
                                clearable=False,
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(["Method:"]),
                                            dcc.Dropdown(
                                                list(directory_dict.keys()),
                                                value=list(directory_dict.keys())[0],
                                                id="method-picker-1",
                                                clearable=False,
                                            ),
                                            html.Label(["Partitioning:"], style={"paddingTop": "8px"}),
                                            dcc.Dropdown(
                                                id="partitioning-picker-1",
                                                clearable=False,
                                            ),
                                            html.Label(["Type:"]),
                                            dcc.Dropdown(
                                                id="type-picker-1",
                                                clearable=False,
                                            ),
                                        ], 
                                        style={"width": "50%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(["Architecture:"], style={"paddingTop": "8px"}),
                                            dcc.Dropdown(
                                                id="architecture-picker-1",
                                                clearable=False,
                                            ),
                                            html.Label(["Metric:"]),
                                            dcc.Dropdown(
                                                list(all_display_options.keys()),
                                                value="CrossEntropyLoss",
                                                id="metric-picker-1",
                                                clearable=False,
                                            ),
                                            html.Label(["Display Type:"]),
                                            dcc.Dropdown(
                                                id="displayType-picker-1",
                                                clearable=False
                                            ),
                                        ],
                                        style={"width": "50%"},
                                    ),
                                ],
                                style={"display": "flex", "gap": "2%"}
                            ),
                        ],
                        style={"display":"flex", "flex-direction":"column", "width":"inherit"}
                    ),

                    # These are the dropdowns for the second graph
                    html.Div(
                        [
                            html.H3("Configuration for Graph 2:"),
                            html.Label(["Dataset:"], style={"paddingTop": "8px"}),
                            dcc.Dropdown(
                                id="dataset-picker-2",
                                clearable=False,
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(["Method:"]),
                                            dcc.Dropdown(
                                                list(directory_dict.keys()),
                                                value=list(directory_dict.keys())[0],
                                                id="method-picker-2",
                                                clearable=False,
                                            ),
                                            html.Label(["Partitioning:"], style={"paddingTop": "8px"}),
                                            dcc.Dropdown(
                                                id="partitioning-picker-2",
                                                clearable=False,
                                            ),
                                            html.Label(["Type:"]),
                                            dcc.Dropdown(
                                                id="type-picker-2",
                                                clearable=False,
                                            ),
                                        ], 
                                        style={"width": "50%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(["Architecture:"], style={"paddingTop": "8px"}),
                                            dcc.Dropdown(
                                                id="architecture-picker-2",
                                                clearable=False,
                                            ),
                                            html.Label(["Metric:"]),
                                            dcc.Dropdown(
                                                list(all_display_options.keys()),
                                                value="CrossEntropyLoss",
                                                id="metric-picker-2",
                                                clearable=False,
                                            ),
                                            html.Label(["Display Type:"]),
                                            dcc.Dropdown(
                                                id="displayType-picker-2",
                                                clearable=False
                                            ),
                                        ],
                                        style={"width": "50%"},
                                    ),
                                ],
                                style={"display": "flex", "gap": "2%"}
                            ),
                        ],
                        style={"display":"flex", "flex-direction":"column", "width":"inherit"}
                    ),
                ],
                style={"display":"flex", "width":"100%", "gap":"5%"}
            ),

            # This is the display for both graphs
            html.Div(
                [
                    html.H3("Graph 1", style={"text-align": "center", "margin": "0", "margin-top":"5%"}),
                    dcc.Graph(
                        id="graph-1",
                        # This figure parameter will be filled by the following code
                        figure={},
                        style={"width": "auto", "height": "45vh"}
                    ),
                    html.H3("Graph 2", style={"text-align": "center", "margin": "0"}),
                    dcc.Graph(
                        id="graph-2",
                        # This figure parameter will be filled by the following code
                        figure={},
                        style={"width": "auto", "height": "45vh"}
                    ),
                ]
            )
        ],
    )

    # This callback is only used for the metric and display type combination and does not need to be changed when the folder structure is updated
    @app.callback(
        [Output("displayType-picker-1", "options"), Output("displayType-picker-1", "value")],
        [Input("metric-picker-1", "value")]
    )
    @app.callback(
        [Output("displayType-picker-2", "options"), Output("displayType-picker-2", "value")],
        [Input("metric-picker-2", "value")]
    )
    def set_display_type_options(selected_metric):
        available_display_types = all_display_options[selected_metric]
        return [{"label": i, "value": i} for i in available_display_types], available_display_types[0]


    # These callbacks control the possible values and default values of the dropdowns based on the provided inputs
    @app.callback(
        [Output("dataset-picker-1", "options"), Output("dataset-picker-1", "value")],
        [Input("method-picker-1", "value")]
    )
    @app.callback(
        [Output("dataset-picker-2", "options"), Output("dataset-picker-2", "value")],
        [Input("method-picker-2", "value")]
    )
    def set_dataset_options(selected_method):
        available_keys = list(directory_dict[selected_method].keys())
        return [{"label": i, "value": i} for i in available_keys], available_keys[0]

    @app.callback(
        [Output("partitioning-picker-1", "options"), Output("partitioning-picker-1", "value")],
        [Input("method-picker-1", "value"), Input("dataset-picker-1", "value")]
    )
    @app.callback(
        [Output("partitioning-picker-2", "options"), Output("partitioning-picker-2", "value")],
        [Input("method-picker-2", "value"), Input("dataset-picker-2", "value")]
    )
    def set_partitioning_options(selected_method, selected_dataset):
        available_keys = list(directory_dict[selected_method][selected_dataset].keys())
        return [{"label": i, "value": i} for i in available_keys], available_keys[0]

    @app.callback(
        [Output("type-picker-1", "options"), Output("type-picker-1", "value")],
        [Input("method-picker-1", "value"), Input("dataset-picker-1", "value"), Input("partitioning-picker-1", "value")]
    )
    @app.callback(
        [Output("type-picker-2", "options"), Output("type-picker-2", "value")],
        [Input("method-picker-2", "value"), Input("dataset-picker-2", "value"), Input("partitioning-picker-2", "value")]
    )
    def set_type_options(selected_method, selected_dataset, selected_partitioning):
        available_keys = list(directory_dict[selected_method][selected_dataset][selected_partitioning].keys())
        return [{"label": i, "value": i} for i in available_keys], available_keys[0]

    @app.callback(
        [Output("architecture-picker-1", "options"), Output("architecture-picker-1", "value")],
        [Input("method-picker-1", "value"), Input("dataset-picker-1", "value"), Input("partitioning-picker-1", "value"), Input("type-picker-1", "value")]
    )
    @app.callback(
        [Output("architecture-picker-2", "options"), Output("architecture-picker-2", "value")],
        [Input("method-picker-2", "value"), Input("dataset-picker-2", "value"), Input("partitioning-picker-2", "value"), Input("type-picker-2", "value")]
    )
    def set_architecture_options(selected_method, selected_dataset, selected_partitioning, selected_type):
        available_keys = list(directory_dict[selected_method][selected_dataset][selected_partitioning][selected_type].keys())
        return [{"label": i, "value": i} for i in available_keys], available_keys[0]

    @app.callback(
        [Output("graph-1", "figure"), Output("graph-2", "figure"),],
        [Input("method-picker-1", "value"), Input("dataset-picker-1", "value"), Input("partitioning-picker-1", "value"), Input("type-picker-1", "value"),
        Input("architecture-picker-1", "value"), Input("metric-picker-1", "value"), Input("displayType-picker-1", "value"),
        Input("method-picker-2", "value"), Input("dataset-picker-2", "value"), Input("partitioning-picker-2", "value"), Input("type-picker-2", "value"),
        Input("architecture-picker-2", "value"), Input("metric-picker-2", "value"), Input("displayType-picker-2", "value"),]
    )
    def display_selected_graph(selected_method_1, selected_dataset_1, selected_partitioning_1, selected_type_1, selected_architecture_1, selected_metric_1,
     selected_display_type_1, selected_method_2, selected_dataset_2, selected_partitioning_2, selected_type_2, selected_architecture_2, selected_metric_2,
     selected_display_type_2):
        # Build path with selected options to match folder structure of a specific result
        selected_result_1 = '\\'.join([selected_method_1, selected_dataset_1, selected_partitioning_1, selected_type_1, selected_architecture_1])
        selected_result_2 = '\\'.join([selected_method_2, selected_dataset_2, selected_partitioning_2, selected_type_2, selected_architecture_2])
        
        # Get index of selected result
        selected_dataframes_index_1 = all_results.get(selected_result_1)
        selected_dataframes_index_2 = all_results.get(selected_result_2)

        # Get dataframe by index and prepare it for displaying
        dataframe_1, header_list_1, values_list_1 = prepare_dataframe_for_displaying(dataframes_per_result, selected_dataframes_index_1, selected_metric_1)
        dataframe_2, header_list_2, values_list_2 = prepare_dataframe_for_displaying(dataframes_per_result, selected_dataframes_index_2, selected_metric_2)

        # Determine which figure to display
        fig_1 = determine_and_create_fig(selected_metric_1, dataframe_1, header_list_1, values_list_1, selected_display_type_1)
        fig_2 = determine_and_create_fig(selected_metric_2, dataframe_2, header_list_2, values_list_2, selected_display_type_2)

        return fig_1, fig_2

    app.run_server(debug=True)

def prepare_dataframe_for_displaying(dataframes_per_result, selected_dataframes_index, selected_metric):
    # Load dataframe by provided index and metric and cleanup
    dataframe = dataframes_per_result[selected_dataframes_index][selected_metric].round(6).fillna(0)
    # Add Index string entry to header_list for the table display so that the index column of the table has a fitting header title
    header_list = ["Index"] + (list(dataframe.columns))
    # Convert every column to an array for later use in the table and individual display
    values_list = [dataframe.index.tolist()] + dataframe.T.values.tolist()
    return dataframe, header_list, values_list