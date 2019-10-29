#! /usr/bin/env python3# Oct26 2019 assignment4HH6
# -*- coding: utf-8 -*-
import dash
import dash_html_components
import dash_core_components
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go


def getData():
	data_link1 = "https://data.cityofnewyork.us/resource/nwxe-4ae8.json"\
	"?$limit=50000&$select=tree_id,spc_common,boroname,health,steward"
	data_frame1 = pd.read_json(data_link1)
	data_link2 = "https://data.cityofnewyork.us/resource/nwxe-4ae8.json"\
	"?$limit=5000&$select=spc_common,health,count(spc_common),boroname"\
	"&$group=spc_common,health,boroname"
	data_frame2 = pd.read_json(data_link2)
	data_frame1.dropna(inplace=True)
	data_frame2.dropna(inplace=True)
	return (data_frame1,data_frame2)

def genrateTable(data_frame):
	html_header = []
	html_data = []
	for column in data_frame.columns:
		html_header.append(dash_html_components.Th(column))
	if len(data_frame)>100:
		for i in range(0,100):
			html_row = []
			for col in data_frame.columns:
				html_row.append(dash_html_components.Td(data_frame.iloc[i][col]))
			html_data.append(dash_html_components.Tr(html_row))
	return dash_html_components.Table([dash_html_components.Tr(dash_html_components.Th(html_header))] + html_data)

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/brPBPO.css'])
server = app.server
app.title = "Assignment 4: Dash NYC Tree"
print("Downloading Data For NYC Tree")
(data_frame,dataset_trees) = getData()
print("Completed Data")

drop_list_species = [{'label': str("AllTreeSpeciesDropDown"), 'value': "All"}]
for trees_type in dataset_trees['spc_common'].unique():
    drop_list_species.append({'label': str(trees_type), 'value': trees_type})

# Create a Dash layout
app.layout = dash_html_components.Div([
    dash_html_components.Div(  ## overall Title
        dash_html_components.H1('HHan Assignment 4: Dash NYC Tree', style={'textAlign': 'center'})
    ),
    dash_core_components.Tabs(id="questions", value='QuestionsTab1', style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
		}, children=[  ## below for Question1 only
        dash_core_components.Tab(label='Question 1', id='tab1', value='QuestionsTab1', children=[
         dash_html_components.Div([dash_html_components.P('How Many TREES by their Conditions?')],style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
                                                       }),   # dropdown for Q1    
            dash_core_components.Dropdown(id='selected_specie', style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
                                                       }, options=drop_list_species, value="AllTreeSpeciesDropDown", multi=False,
                         placeholder="Please Choose a specie of tree")
            , dash_html_components.Div(id='representation')
        ]),  ## below for Question2 only
        dash_core_components.Tab(label='Question 2', id='tab2', value='QuestionsTab2', children=[
			dash_html_components.Div([dash_html_components.P('Health of TREES by Stewardess?')],style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
                           }),          ## Dropdown menu for Q2
          dash_core_components.Dropdown(id='drpdwn2', style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
                                                       }, options=drop_list_species, value="AllTreeSpeciesDropDown", multi=False,
                         placeholder="Please Choose a specie of tree"),
         ## create a table for Q2
            dash_html_components.Div([genrateTable(data_frame)], style={'margin': 'auto',
    'width': '80%','textAlign': 'center'
                                                       })
        ])
    ])
])


@app.callback(Output(component_id='representation', component_property='children'),
              [Input(component_id='selected_specie', component_property='value')])
              
def trees_figure_update(selected_species):
    picture = []
    if selected_species == "AllTreeSpeciesDropDown":
        selected_family = dataset_trees
    else:
        selected_family = dataset_trees[dataset_trees['spc_common'] == selected_species]
    picture.append(dash_html_components.Div(dash_core_components.Graph(
        id=selected_species,
        figure={
            'data': [
                {'x': selected_family[selected_family['health'] == 'Good'].boroname,
                 'y': selected_family[selected_family['health'] == 'Good']['count_spc_common'], 'type': 'bar', 'name': 'Health: Good'},
                {'x': selected_family[selected_family['health'] == 'Fair'].boroname,
                 'y': selected_family[selected_family['health'] == 'Fair']['count_spc_common'], 'type': 'bar', 'name': 'Health: Fair'},
                {'x': selected_family[selected_family['health'] == 'Poor'].boroname,
                 'y': selected_family[selected_family['health'] == 'Poor']['count_spc_common'], 'type': 'bar', 'name': 'Health: Poor'},
            ],
            'layout': {
                'title': 'Graphical DISPLAY of ' + selected_species
            }
        }
    )))
    return picture
    
if __name__ == '__main__':
    app.run_server(debug=True)
