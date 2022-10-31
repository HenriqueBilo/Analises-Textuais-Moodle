import dash
import dash_table
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = px.data.tips()

path = ["day", "time", "sex"]

app.layout = html.Div(
    [
        html.H4(id="title"),
        html.Div(
            [
                dcc.Graph(
                    id="sunburst",
                    figure=px.sunburst(df, path=path, values="total_bill"),
                )
            ]
        ),
        html.Div(
            [
                dash_table.DataTable(
                    id="table",
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                    sort_action="native",
                )
            ]
        ),
    ]
)


@app.callback(
    [
        Output("table", "data"),
        Output("table", "style_data_conditional"),
        Output("title", "children"),
    ],
    [Input("sunburst", "clickData"), Input("sunburst", "hoverData")],
)
def update_table(clickData, hoverData):

    click_path = "ALL"
    root = False
    data = df.to_dict("records")

    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"]

    style_data_conditional = []
    if hoverData:
        hover_path = hoverData["points"][0]["id"].split("/")       
        if len(hover_path) == 1:
            selected = [hover_path[0], "none", "none"]
        elif len(hover_path) == 2:
            selected = [hover_path[0], hover_path[1], "none"]
        else:
            selected = hover_path

        style_data_conditional = [
            {
                "if": {
                    "filter_query": "{{day}} = {}".format(selected[0]),
                    "column_id": "day",
                },
                "backgroundColor": "#ffe0de",
                "color": "white",
            },
            {
                "if": {
                    "filter_query": "{{time}} = {}".format(selected[1]),
                    "column_id": "time",
                },
                "backgroundColor": "#e0deff",
                "color": "white",
            },
            {
                "if": {
                    "filter_query": "{{sex}} = {}".format(selected[2]),
                    "column_id": "sex",
                },
                "backgroundColor": "#deffe0",
            },
        ]

    if input_id == "sunburst.clickData":
        style_data_conditional = []
        click_path = clickData["points"][0]["id"].split("/")

        selected = dict(zip(path, click_path))

        if "sex" in selected:
            dff = df[
                (df["day"] == selected["day"])
                & (df["time"] == selected["time"])
                & (df["sex"] == selected["sex"])
            ]
        elif "time" in selected:
            dff = df[(df["day"] == selected["day"]) & (df["time"] == selected["time"])]
        else:
            dff = df[(df["day"] == selected["day"])]
            root = True
        data = dff.to_dict("records")

        # Show all data when returning to the root from an outer leaf
        percentEntry = (clickData["points"][0]).get("percentEntry")
        if root and percentEntry == 1:
            data = df.to_dict("records")
            click_path = "ALL"

    title = f"Selected From Sunburst Chart: {' '.join(click_path)}"

    return data, style_data_conditional, title


if __name__ == "__main__":
    app.run_server(debug=True)