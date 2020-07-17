import dash   
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.express as px 
import pandas as pd

from dash.dependencies import Input, Output

def read_posdata(path):
    df = pd.read_table(path, encoding='utf-16', header=[1,2,3,4,5])
    df = df.melt(id_vars=[df.columns[0]])
    df.columns = ['date', 'area', 'store', 'huge', 'mid', 'type', 'value']
    return df

df = read_posdata('data/pos_data_0706.csv')

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    
    dcc.RadioItems(
        id = 'my_radio',
        options = [{"label": t, "value": t} for t in df.type.unique()],
        value = '販売金額指数'
    ),
    
    html.Div(id='my_body',
        

    )
    
])

@app.callback(Output('my_body', 'children'), [Input('my_radio', 'value')])
def update_body(selected_value):
    if selected_value == '前年比（％）':
        
        return html.Div()
    
    else:
        index_body = html.Div([
            
            dcc.Dropdown(
                id='drop_one',
                options=[{'label': a, 'value': a} for a in df.area.unique()],
                value=df.area.unique()[0]
                    ),
            dcc.Dropdown(id='drop_two'),
            dcc.Dropdown(id='drop_thr'),
            dcc.Dropdown(id='drop_four'),
            dcc.Graph(id='my_graph')
            
        ])
        
        
        return index_body
    
@app.callback([Output('drop_two', 'options'), 
               Output('drop_two', 'value')],
               [Input('drop_one', 'value')])
def update_drop_two(selected_value):
    df1 = df[df['area'] == selected_value]
    
    return [{'label': st, 'value': st} for st in df1['store'].unique()], df1['store'].unique()[0]

@app.callback([Output('drop_thr', 'options'),
              Output('drop_thr', 'value')],
              [Input('drop_two', 'value')]
             )
def update_drop_three(selected_value):
    df1 = df[df['store'] == selected_value]
    
    return [{'label': h, 'value': h} for h in df1['huge'].unique()], df1['huge'].unique()[0]

@app.callback([Output('drop_four', 'options'),
              Output('drop_four', 'value'),
              Output('drop_four', 'multi')
              ],
             [Input('drop_thr', 'value')]
             )
def update_drop_four(selected_value):
    df1 = df[df['huge'] == selected_value]
    
    return [{'label': h, 'value': h} for h in df1['mid'].unique()], [df1['mid'].unique()[0]], True

@app.callback(Output('my_graph', 'figure'), 
              [Input('drop_one', 'value'),
               Input('drop_two', 'value'),
               Input('drop_thr', 'value'),
               Input('drop_four', 'value'),
              Input('my_radio', 'value')
              ])
def update_graph(selected_one, selected_two, selected_three, selected_four, radio_value):
    df1 = df[df['area'] == selected_one]
    df2 = df1[df1['store'] == selected_two]
    df3 = df2[df2['huge'] == selected_three]
    df4 = df3[df3['type'] == radio_value]
    df5 = df4[df4['mid'].isin(selected_four)]
    
    return px.line(df5, x='date', y='value', color='mid')

if __name__ == "__main__":
    app.run_server(debug=True)
    
