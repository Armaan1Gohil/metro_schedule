import dash
from dash import Dash, html, dcc, Input, State, Output, ALL, Patch  # pip install dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc   # pip install dash-bootstrap-components
import pandas as pd     # pip install pandas
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import threading

matplotlib_lock = threading.Lock()

def generate_matplotlib_graph(headway, dwell_time, station_name, station_dis):
    with matplotlib_lock:
        no_of_trains = 2*(len(station_dis))  # No of trains running
        train_data = {}

        # Generating points for graph
        for train in range(no_of_trains):
            train_data[f'x{train}'] = []
            train_data[f'y{train}'] = []

            ## Generating points for up line
            
            # Generates y-axis points
            for station_index, dis in enumerate(station_dis): 
                if dis == station_dis[-1]: # Helps to prevent IndexError
                    break
                for dis_travel in range(dis, station_dis[station_index+1]+1): # Generate slope points
                    train_data[f'y{train}'].append(dis_travel)
                
                if dis == station_dis[-2]: # Helps to prevent IndexError
                    break
                for _ in range(dwell_time-1): # Generating horizontal points
                    train_data[f'y{train}'].append(station_dis[station_index+1])
                    

            # Generates x-axis points
            for l in range(len(train_data[f'y{train}'])): # Change with considering headway
                train_data[f'x{train}'].append(l + train*(headway))
            
            down_train = train + no_of_trains
            ## Generating points for down line
            train_data[f'x{down_train}'] = [] 
            train_data[f'y{down_train}'] = []
            train_data[f'x{down_train}'] = train_data[f'x{train}'] # Generates x-axis points
            train_data[f'y{down_train}'] = train_data[f'y{train}'][::-1] # Generates y-axis points

        fig, ax1 = plt.subplots(figsize=(9,6)) # Creating subplots
        ax1.set_xticks(np.arange(0, train_data['x0'][-1]+1)) #Select ticks

        # Axis lable and title
        ax1.set_xlabel('Time (minutes)')
        ax1.set_ylabel('Chainage (km)')
        ax1.set_title('Train Schedule')

        # Plot uplines
        for i in range(no_of_trains):
            ax1.plot(train_data[f'x{i}'], train_data[f'y{i}'], color='#1f77b4')

        # Plot downlines
        for i in range(no_of_trains, no_of_trains*2):
            ax1.plot(train_data[f'x{i}'], train_data[f'y{i}'], color='#ff7f0e')

            
        # Add grey line for stations
        for station in station_dis: 
            x = list(np.arange(0, train_data[f'x{no_of_trains-1}'][-1] + 1))
            y = [station]*(train_data[f'x{no_of_trains-1}'][-1] + 1)
            ax1.plot(x, y, alpha=0.1, linewidth=7.5, color='#a2a2a1')

        ax2 = ax1.twinx()
        ax1.set_xticks(np.arange(0, train_data[f'x{no_of_trains-1}'][-1]+1, step=headway))
        ax1.set_xticklabels(np.arange(0, train_data[f'x{no_of_trains-1}'][-1]+1, step=headway))
        ax1.set_ylim([0, station_dis[-1]])
        ax1.set_yticks(np.arange(0, station_dis[-1]+1))
        ax2.set_ylim([0, station_dis[-1]])
        ax2.set_yticks(station_dis)
        ax2.set_yticklabels(station_name)
        ax1.grid(axis = "x", linestyle='dashed', linewidth=1.5, alpha=0.25)

        # Save it to a temporary buffer
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        return buf.read()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
 
app.title = 'Train Schedule' 
 
app.layout = dbc.Container(
    [   
        html.Br(),
        dbc.Card(
            [
                dbc.CardHeader(html.H1('Metro Train Schedule Graph')),
                dbc.CardBody(
                 [
                dbc.Row(
                [
                    dbc.Col(dbc.Label("Number of Stations"), lg=2, sm=12, className='text-lg-right'),
                    dbc.Col(dbc.Input(type="number", id="no_of_stations", placeholder="Enter Number of Stations", style={'margin-bottom': '0.5rem'}, required=True), lg=4, sm=12),
                    dbc.Col(dbc.Button("Create", color="primary", id='button_click'), lg=1, sm=12),
                ], className='row text-center justify-content-center'),
        ]),
    ],),
        html.Div([
            # Enter headway and dwell time
            html.Br(),
            html.H3('Headway and Dwell Time:'),
            dbc.Row([
                dbc.Col(dbc.Label('Headway'), lg=2, sm=12, className='text-lg-right'),
                dbc.Col(dbc.Input(type='number', placeholder='Enter Headway (In Min)', id='headway', required=True), lg=4, sm=12),
                dbc.Col(dbc.Label('Dwell Time'), lg=2, sm=12, className='text-lg-right'),
                dbc.Col(dbc.Input(type='number', placeholder='Enter Dwell Time (In Min)', id='dwell_time', required=True), lg=4, sm=12),
            ], justify='center', align='center'),
            html.Br()
    ]),
        html.Div(id='add_stations', children=[]),
        html.Br(),
        html.Div(html.Img(id='graph'), className='text-center'),
        html.Div(id='error_handle', children=[]),
    ]
)

# For creating station inputs
@app.callback(
    Output(component_id='add_stations', component_property='children'),
    Input(component_id='button_click', component_property='n_clicks'),
    State(component_id='no_of_stations', component_property='value'),
    prevent_initial_call=True
)
def update_output(n_clicks, no_of_stations):
    print(no_of_stations)
    if no_of_stations is None or no_of_stations == '':
        return(dbc.Row(dbc.Col(dbc.Alert('Number of Stations is Empty!', color='danger')))) # Error if staions are less than 2    
    elif no_of_stations < 2: # Stations cannot be less than 1
        return(dbc.Row(dbc.Col(dbc.Alert('Error: Enter a Value Greater than 2!', color='danger')))) # Error if staions are less than 2
    else:
        stations = Patch()
        stations.clear()
        # Creates the inputs for station name and chainage depending on the number of stations
        stations.append(html.Hr())
        stations.append(html.H3('Enter Station and Chainage Details:'))
        stations.append(html.P(html.I('Start Chainage from zero')))
        for i in range(no_of_stations):
            stations.append(
                dbc.Row([
                    dbc.Col(dbc.Label('Station Name'), lg=2, sm=12, className='text-lg-right'),
                    dbc.Col(dbc.Input(type='text', placeholder=f'Enter Station Name {i+1}', id={'type': 'station_name_value', 'index': i}, required=True), lg=4, sm=12),
                    dbc.Col(dbc.Label('Chainage'), lg=2, sm=12, className='text-lg-right'),
                    dbc.Col(dbc.Input(type='number', placeholder=f'Enter Chainage {i+1} (In Km)', id={'type': 'chainage_num_value', 'index': i}, required=True), lg=4, sm=12), 
                ], style={'margin-bottom': '0.5rem'}),
            )
        stations.append(html.Br())
        stations.append(html.Div(dbc.Button("Generate Graph", color='primary', id={'type': 'create_button', 'index': 1}), className='text-center')) # Button to generate graph
        return stations
                

@app.callback(
     Output('graph', 'src'),
     Output('error_handle', 'children'),
     Input({'type': 'create_button', 'index': ALL}, 'n_clicks'),
     [State('headway', 'value'),
     State('dwell_time', 'value'),
     State({'type': 'station_name_value', 'index': ALL}, 'value'),
     State({'type': 'chainage_num_value', 'index': ALL}, 'value')],
     prevent_initial_call = True,
)
def plot_graph(n_clicks, headway, dwell_time, station_name, station_dis):
    if any(n_clicks):
        if headway is None or dwell_time is None or station_name is None or station_dis is None:
            return None, (dbc.Row(dbc.Col(dbc.Alert('Check Empty Input!', color='danger')))) # Error if staions are less than 2    
        else:
            fig_bytes = generate_matplotlib_graph(headway, dwell_time, station_name, station_dis)
            fig_base64 = base64.b64encode(fig_bytes).decode('utf-8')
            return f'data:img/png;base64, {fig_base64}', None

if __name__ == '__main__':
    app.run_server(debug=False, threaded=True, port=8002)
