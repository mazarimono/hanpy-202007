import ast
import os 

import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import dash  
import dash_core_components as dcc 
import dash_html_components as html

from dash.dependencies import Input, Output

df = pd.read_table('data/pos_data_0706.csv', encoding='utf-16', header=[1,2,3,4,5], index_col=0)
df.columns.names = ('area', 'shop', 'class', 'product', 'type')
col_data = df.columns.to_frame()
col_data = col_data[['type', 'area', 'shop', 'class', 'product']].values
col_df = pd.DataFrame(col_data)
col_df = pd.MultiIndex.from_frame(col_df, names=['type', 'area', 'shop', 'class', 'product'])
df.columns = col_df
df = df.sort_index()
df_index = df['販売金額指数']
df_yoy = df["前年比（％）"]

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True 

server = app.server 

app.layout = html.Div([
    
    dcc.RadioItems(
        id="my_radio",
        options = [{"label": col, "value": col} for col in col_df.get_level_values(0).unique()],
        value = col_df.get_level_values(0).unique()[0]
    ),
    
    
    html.Div(id="switch_layout")
    
], style={"width": 1200})

@app.callback(Output("switch_layout", "children"), 
              [Input("my_radio", "value")])
def update_graph(radio_select):
    if radio_select == "前年比（％）":
        yoy_layout = html.Div([
            
            dcc.Dropdown(
                id="my_dropdown2",
                options = [{"label": dat, 'value': dat} for dat in df_yoy.index],
                value = [df_yoy.index[-1]],
                multi=True
            ),
            
            dcc.Dropdown(
                id="select_area",
                options=[{"label": area_s, "value": area_s} for area_s in col_df.get_level_values(1).unique()],
                value = col_df.get_level_values(1).unique()[0],
                #multi = True
            ),
            
            dcc.Graph(id="my_graph2"),
            #html.Div(id="my_graph2")
            
        ])
        return yoy_layout
    else:
        index_layout = html.Div([
            html.Div([
            dcc.Dropdown(
                id="my_dropdown",
                options = [{"label": f"{col}", 'value': f"{col}"} for col in df_index.columns],
                value = [f"{df_index.columns[0]}"],
                multi=True
            ),], style={"margin": "auto", "width": "60%"}),
            dcc.Graph(id="my_graph")
            
        ], style={"width": "100%"})
        return index_layout
    
@app.callback(Output("my_graph2", "figure"), [Input("my_dropdown2", "value"), Input("select_area", "value")])
def update_pct_graph(selected_date, selected_area):
    if selected_area == "00_全国":
        df_yoy_selected = df_yoy[df_yoy.index.isin(selected_date)]
        df_yoy_selected = df_yoy_selected[selected_area]
    
        fig = go.Figure()
        for i in range(len(df_yoy_selected)):
            fig.add_trace(go.Bar(x=df_yoy_selected.columns.get_level_values(-1), y=df_yoy_selected.iloc[i-1, :], name=df_yoy_selected.index[i-1]))
    
        return fig

@app.callback(Output("my_graph", "figure"), [Input("my_dropdown", "value")])
def update_index_graph(selected_value):
    fig = go.Figure()
    for val in selected_value:
        ast_value = ast.literal_eval(val)
        fig.add_trace(go.Scatter(x=df_index.index, y=df_index[ast_value], name=f"{ast_value[0]}/{ast_value[1]}/{ast_value[3]}"))
    fig.update_layout(height=800)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
