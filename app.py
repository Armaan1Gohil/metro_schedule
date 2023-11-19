import dash
from dash import Dash, html, dcc, Input, State, Output, ALL, Patch  # pip install dash
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc   # pip install dash-bootstrap-components
import pandas as pd     # pip install pandas
import numpy as np

def generate_graph(headway, dwell_time, station_name, station_dis):
    no_of_trains = (len(station_dis))  # No of trains running

    # Generating points for graph
    train_data_x = []
    train_data_y = []

    ## Generating points for up line
    # Generates y-axis points
    for station_index, dis in enumerate(station_dis): 
        if dis == station_dis[-1]: # Helps to prevent IndexError
            break
        for dis_travel in range(dis, station_dis[station_index+1]): # Generate slope points
            train_data_y.append(dis_travel)

        for _ in range(dwell_time-1): # Generating horizontal points
            train_data_y.append(station_dis[station_index+1])


    # Generates x-axis points
    for l in range(len(train_data_y)):
        train_data_x.append(l)

    ## Generating points for down line
    train_oppo_x = train_data_x # Generates x-axis points
    train_oppo_y = train_data_y[::-1] # Generates y-axis points
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # # Plot up lines & down lines
    fig.add_trace(
        go.Scatter(x=train_data_x, y=train_data_y, mode='lines', showlegend=False, name='Upline', line=dict(color='#1f77b4'))
    ) # Plot up lines

    fig.add_trace(
        go.Scatter(x=train_oppo_x, y=train_oppo_y, mode='lines',  showlegend=False, name='Downline', line=dict(color='#ff7f0e'))
    ) # Plot down lines


    # Add grey line for stations
    for i, station in enumerate(station_dis): 
        x_secondary = [train_data_x[0],train_data_x[-1]]
        y_secondary = [station, station]

        line_color = 'rgba(162, 162, 161, 0.2)'
        fig.add_trace(
            go.Scatter(x=x_secondary, y=y_secondary, mode='lines', name=station_name[i], showlegend=False, line=dict(color=line_color, width=8),
                    ),
            secondary_y=True
        ) # Plot station lines

        # Plot fills
        i = headway
        while i < train_data_x[-1]:
            # Plot up line fills
            train_fill_x = train_data_x[i:]
            train_fill_y = train_data_y[0:-i]

            fig.add_trace(
                go.Scatter(x=train_fill_x, y=train_fill_y, mode='lines', showlegend=False, name='Upline', line=dict(color='#1f77b4'))
            ) # Plot up lines
            
            train_fill_x_up = train_data_x[0:-i]
            train_fill_y_up = train_data_y[i:]
            fig.add_trace(
                go.Scatter(x=train_fill_x_up, y=train_fill_y_up, mode='lines', showlegend=False, name='Upline', line=dict(color='#1f77b4'))
            ) # Plot up lines
            
            # Plot down line fills
            train_fill_oppo_x_up = train_oppo_x[i:]
            train_fill_oppo_y_up = train_oppo_y[0:-i]
            
            fig.add_trace(
            go.Scatter(x=train_fill_oppo_x_up, y=train_fill_oppo_y_up, mode='lines',  showlegend=False, name='Downline', line=dict(color='#ff7f0e'))
            ) # Plot down lines
            
            train_fill_oppo_x = train_oppo_x[0:-i]
            train_fill_oppo_y = train_oppo_y[i:]
            
            fig.add_trace(
            go.Scatter(x=train_fill_oppo_x, y=train_fill_oppo_y, mode='lines',  showlegend=False, name='Downline', line=dict(color='#ff7f0e'))
            ) # Plot down lines
            
            i += headway

    # Create legend entries for "upline" and "downline"
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='#1f77b4'), name='Upline'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='#ff7f0e'), name='Downline')) 
        
    # Axis lable and title
    fig.update_yaxes(
        title_text='Station Name',
        tickmode='array',
        tickvals=station_dis,
        ticktext=station_name,
        ticks='outside',
        linecolor='lightgrey',
        secondary_y=True  # This makes it the second y-axis
    )

    fig.update_layout(
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(itemsizing='constant', x=0, y=-0.2),
        
        scene=dict(aspectmode='cube'),
        height=750,

        title_text='Train Schedule',
        
        xaxis=dict(
            mirror=True,
            gridcolor='lightgrey',
            showline=True,
            linecolor='lightgrey',
            title=dict(text='Time in Minutes'),
            ticks='outside',
            tickmode='array',
        ),
        
        yaxis=dict(
            title=dict(text='Chainage (km)'),
            tickmode='array',
            tickvals=station_dis,
            ticks='outside',
            linecolor='lightgrey',
        ),
    )

    return fig

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
 
app.title = 'Train Schedule'
 
app.layout = dbc.Container(
    [   
        html.Script(type='text/javascript', children=[
            '''
                (function(c,l,a,r,i,t,y){
                    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
                })(window, document, "clarity", "script", "jhgwrliuco");
            '''
            ]), 
        html.Br(),
        dbc.Card(
            [
                dbc.CardHeader(html.H1('Metro Train Schedule Graph')),
                dbc.CardBody(
                 [
                dbc.Row(
                [
                    dbc.Col(dbc.Label("Number of Stations"), lg=2, sm=12, className='text-lg-right'),
                    dbc.Col(dbc.Input(type="number", id="no_of_stations", placeholder="Enter Number of Stations", style={'margin-bottom': '0.5rem'}), lg=4, sm=12),
                    dbc.Col(dbc.Button("Create Stations", color="primary", id='button_click'), lg=2, sm=12),
                ], className='row text-center justify-content-center'),
        ]),
    ],),
        html.Div([
            # Enter headway and dwell time
            html.Br(),
            html.H3('Headway and Dwell Time:'),
            dbc.Row([
                dbc.Col(dbc.Label('Headway'), lg=2, sm=12, className='text-lg-right'),
                dbc.Col(dbc.Input(type='number', placeholder='Enter Headway (In Min)', id='headway', required=True, style={'margin-bottom': '1rem'}), lg=4, sm=12),
                dbc.Col(dbc.Label('Dwell Time'), lg=2, sm=12, className='text-lg-right'),
                dbc.Col(dbc.Input(type='number', placeholder='Enter Dwell Time (In Min)', id='dwell_time', required=True, style={'margin-bottom': '1rem'}), lg=4, sm=12),
            ], justify='center', align='center'),
            html.Br()
    ]),
        html.Div(id='add_stations', children=[]),
        html.Br(),
        dcc.Graph(id='graph', style={'visibility': 'hidden'}),
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
                    dbc.Col(dbc.Input(type='text', placeholder=f'Enter Station Name {i+1}', id={'type': 'station_name_value', 'index': i}, required=True, style={'margin-bottom': '1rem'}), lg=4, sm=12),
                    dbc.Col(dbc.Label('Chainage'), lg=2, sm=12, className='text-lg-right'),
                    dbc.Col(dbc.Input(type='number', placeholder=f'Enter Chainage {i+1} (In Km)', id={'type': 'chainage_num_value', 'index': i}, required=True), style={'margin-bottom': '1rem'}, lg=4, sm=12), 
                ], style={'margin-bottom': '1rem'}),
            )
        stations.append(html.Br())
        stations.append(html.Div(dbc.Button("Generate Graph", color='primary', id={'type': 'create_button', 'index': 1}), className='text-center')) # Button to generate graph
        return stations

@app.callback(
     Output('graph', 'figure'),
     Output('graph', 'style'),
     Input({'type': 'create_button', 'index': ALL}, 'n_clicks'),
     [State('headway', 'value'),
     State('dwell_time', 'value'),
     State({'type': 'station_name_value', 'index': ALL}, 'value'),
     State({'type': 'chainage_num_value', 'index': ALL}, 'value')],
     prevent_initial_call = True,
)
def plot_graph(n_clicks, headway, dwell_time, station_name, station_dis):
    if n_clicks[0] is None:
        raise PreventUpdate
    else:
        graph_fig = generate_graph(headway, dwell_time, station_name, station_dis)
        return graph_fig, {'style': 'visible'}

if __name__ == '__main__':
    app.run_server(debug=False, threaded=True, port=8002)
