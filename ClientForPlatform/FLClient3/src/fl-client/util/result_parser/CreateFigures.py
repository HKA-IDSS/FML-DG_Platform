import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Check which metric was selected in the dropdowns and determine which function to use for these type of dataframes
def determine_and_create_fig(selected_metric, dataframe, header_list, values_list, selected_display_type):
    if selected_metric == "CrossEntropyLoss" or selected_metric == "Accuracy" or selected_metric == "MCC":
        return create_sv_fig(dataframe, header_list, values_list, selected_display_type)

    elif selected_metric == "F1Score":
        return create_f1_score_fig(dataframe, selected_display_type)

    elif selected_metric == "ClientLabels" or selected_metric == "TestingLabels":
        return create_labels_fig(dataframe, header_list, values_list, selected_display_type)

    elif selected_metric == "GlobalAccuracyAndLoss" or selected_metric == "GlobalF1Score":
        return create_global_fig(dataframe, header_list, values_list, selected_display_type)


def create_sv_fig(df, header_list, values_list, selected_display_type):
    if selected_display_type == "Aggregated":
        fig = px.bar(
            # df.loc[["aggregated", "server"]].T,
            df.loc[["aggregated", "server"]],
            barmode="group",
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig
    
    elif selected_display_type == "Individual":
        fig = px.bar(
            # df.T[values_list[0]],
            df.loc[values_list[0]],
            barmode="group",
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig
    
    elif selected_display_type == "Scatter":
        # fig = px.scatter(df.loc[["aggregated", "server"]].T)
        fig = px.scatter(df.loc[["aggregated", "server"]])
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig
    
    elif selected_display_type == "Table":
        # Use graph objects for tables because plotly express does not provide them
        fig = go.Figure(
            data=[
                go.Table(
                columnwidth=[250,400,400],
                header=dict(values=header_list),
                cells=dict(values=values_list)
                )
            ]
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return fig


# Special treatment for F1Score because plotly express does not support multi-indexing yet
def create_f1_score_fig(df, selected_display_type):
    # Split multi-index into two seperate columns and add basic index column in the beginning
    f1_score_df = df.reset_index().round(decimals=6)
    # Add Index string entry to header_list for the table display so that the index column of the table has a fitting header title
    header_list = ["Index"] + (list(f1_score_df.columns))
    # Convert every column to an array for later use in the table display
    values_list = [f1_score_df.index.tolist()] + f1_score_df.T.values.tolist()
    # Save names of columns that are not indexes
    columns = f1_score_df.columns[2:]

    # Use subplots as a base to display multi-indexes
    fig = make_subplots(rows=1, cols=1)

    if selected_display_type == "Aggregated" or selected_display_type == "Individual":
        # Iterate over every column that is not an index
        for col in columns:
            # Add bar graph object to the subplot
            fig.add_trace(
                go.Bar(
                    # Add first (Evaluator) and second (Class_number) index of multi-index for correct display to x-axis
                    x=[f1_score_df['Evaluator'], f1_score_df['Class_number']],
                    # Add iterated column values that are not indexes to y-axis
                    y=f1_score_df[col],
                    name=col,
                    legendgroup=col,
                    showlegend=True,
                ),
                row=1,
                col=1
            )
            
        if selected_display_type == "Aggregated":
            # Use barmode relative so that the bars stack and don't overlap, otherwise they will be displayed individually
            fig.update_layout(barmode="relative")
        
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return fig
    
    elif selected_display_type == "Scatter":
        # Iterate over every column that is not an index
        for col in columns:
            # Add scatter graph object to the subplot
            fig.add_trace(
                go.Scatter(
                    # Add first (Evaluator) and second (Class_number) index of multi-index for correct display to x-axis
                    x=[f1_score_df['Evaluator'], f1_score_df['Class_number']],
                    # Add iterated column values that are not indexes to y-axis
                    y=f1_score_df[col],
                    name=col,
                    legendgroup=col,
                    showlegend=True,
                    mode="markers"
                ),
                row=1,
                col=1
            )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return fig
    
    elif selected_display_type == "Table":
        # Use graph objects for tables because plotly express does not provide them
        table_fig = go.Figure(
            data=[
                go.Table(
                    columnwidth=[250,400,400],
                    header=dict(values=header_list),
                    cells=dict(values=values_list)
                )
            ]
        )
        # Apply some styling so that the figures don't interfere
        table_fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return table_fig


def create_labels_fig(df, header_list, values_list, selected_display_type):
    if selected_display_type == "Aggregated":
        fig = px.bar(df)
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig

    elif selected_display_type == "Individual":
        fig = px.bar(
            df,
            barmode="group",
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig

    elif selected_display_type == "Table":
        # Use graph objects for tables because plotly express does not provide them
        fig = go.Figure(
            data=[
                go.Table(
                    columnwidth=[250,400,400],
                    header=dict(values=header_list),
                    cells=dict(values=values_list)
                )
            ]
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return fig


def create_global_fig(df, header_list, values_list, selected_display_type):
    if selected_display_type == "Aggregated":
        fig = px.bar(
            df.loc[["aggregated"]],
            barmode="group",
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig

    elif selected_display_type == "Per Round":
        fig = px.line(df.iloc[:-1])
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        return fig

    elif selected_display_type == "Table":
        # Use graph objects for tables because plotly express does not provide them
        fig = go.Figure(
            data = [
                go.Table(
                    columnwidth=[250,400,400],
                    header=dict(values=header_list),
                    cells=dict(values=values_list)
                )
            ]
        )
        # Apply some styling so that the figures don't interfere
        fig.update_layout(margin=dict(l=70,r=150,b=0,t=20))
        return fig