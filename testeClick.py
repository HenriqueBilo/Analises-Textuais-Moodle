# import modules    
import json    
import pandas as pd    
import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

# prepare dash_table    
size = 5
df = pd.DataFrame([], index=range(size))
df['num'] = range(size)
df['char'] = list('abcdefghijk')[:size]    
tab = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    tooltip_data=[
        {
            # (B) multiply cell value by 10 for demonstration purpose
            column: {'value': str(value*10), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df.to_dict('records')
    ],
    tooltip_delay=0,
    tooltip_duration=None
)

# set layout    
app = dash.Dash('SimpleExample')     
app.layout = html.Div([
    tab,
    html.Div(id='click-data', style={'whiteSpace': 'pre-wrap'}),

])

# define callback        
@app.callback(
    Output('click-data', 'children'),
    [Input('table', 'active_cell')],
     # (A) pass table as data input to get current value from active cell "coordinates"
    [State('table', 'data')]
)
def display_click_data(active_cell, table_data):
    if active_cell:
        cell = json.dumps(active_cell, indent=2)    
        row = active_cell['row']
        col = active_cell['column_id']
        value = table_data[row][col]
        out = '%s\n%s' % (cell, value)
    else:
        out = 'no cell selected'
    return out
 
# run app    
if __name__ == '__main__':
    app.run_server(debug=True)