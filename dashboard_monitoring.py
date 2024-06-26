import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

def load_temperature_data(file_path):
    return pd.read_csv(file_path, delimiter=';')

def load_cpu_data(file_path):
    return pd.read_csv(file_path, delimiter=';')

def dashboard(df_temp, df_cpu):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Dashboard from thermal zones", className='text-center text-primary mb-4'), width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Selecione a zona térmica:", className='font-weight-bold'),
                dcc.Dropdown(
                    id='zone-dropdown',
                    options=[{'label': col, 'value': col} for col in df_temp.columns if 'zone' in col],
                    value=df_temp.columns[2],  
                    className='mb-4'
                ),
            ], width=4),
            dbc.Col([
                html.Label("Intervalo de tempo inicial (HH:MM):", className='font-weight-bold'),
                dcc.Input(id='initial-time', type='text', value='00:00', className='form-control mb-4')
            ], width=4),
            dbc.Col([
                html.Label("Intervalo de tempo final (HH:MM):", className='font-weight-bold'),
                dcc.Input(id='final-time', type='text', value='23:59', className='form-control mb-4')
            ], width=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Selecione o dia (YYYY-MM-DD):", className='font-weight-bold'),
                dcc.Input(id='day', type='text', value='2024-05-20', className='form-control mb-4')
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='temperature-graph', style={'backgroundColor': '#f8f9fa'}), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='alert-message', style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}), width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Selecione o CPU:", className='font-weight-bold'),
                dcc.Dropdown(
                    id='cpu-dropdown',
                    options=[{'label': col, 'value': col} for col in df_cpu.columns if col.startswith('cpu')],
                    value=df_cpu.columns[2],
                    multi=True,
                    className='mb-4'
                ),
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='cpu-usage-graph', style={'backgroundColor': '#f8f9fa'}), width=12)
        ]),
    ], fluid=True)

    @app.callback(
        [Output('temperature-graph', 'figure'),
         Output('alert-message', 'children')],
        [Input('zone-dropdown', 'value'),
         Input('initial-time', 'value'),
         Input('final-time', 'value'),
         Input('day', 'value')]
    )
    def update_temperature_graph(selected_zone, initial_time_interval, final_time_interval, day):
        limite_temperatura = 40
        df_filtered = df_temp[(df_temp['day'] == day) & (df_temp['time'] >= initial_time_interval) & (df_temp['time'] <= final_time_interval)]

        fig = px.line(df_filtered, x='time', y=selected_zone, title=f'Temperatura na {selected_zone} na data {day}')
        fig.update_layout(
            xaxis_title='Horario do dia',
            yaxis_title='Temperatura em C°',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black'),
            title_font=dict(size=20, color='black', family='Arial'),
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='black',
                linewidth=2,
                ticks='outside',
                tickfont=dict(family='Arial', size=12, color='black'),
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='black',
                linewidth=2,
                ticks='outside',
                tickfont=dict(family='Arial', size=12,color='black'),
            )
        )

        alert_msg = ""
        if df_filtered[selected_zone].max() > limite_temperatura:
            alert_msg = f"ALERTA: A temperatura na zona térmica {selected_zone} excedeu o limite!"

        return fig, alert_msg

    @app.callback(
        Output('cpu-usage-graph', 'figure'),
        [Input('cpu-dropdown', 'value'),
         Input('initial-time', 'value'),
         Input('final-time', 'value'),
         Input('day', 'value')]
    )
    def update_cpu_usage_graph(selected_cpus, initial_time_interval, final_time_interval, day):
        df_cpu_filtered = df_cpu[(df_cpu['day'] == day) & (df_cpu['time'] >= initial_time_interval) & (df_cpu['time'] <= final_time_interval)]
        
        fig = px.line(df_cpu_filtered, x='time', y=selected_cpus, title=f'Consumo de CPU na data {day}')
        fig.update_layout(
            xaxis_title='Horario do dia',
            yaxis_title='Uso de CPU (%)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black'),
            title_font=dict(size=20, color='black', family='Arial'),
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='black',
                linewidth=2,
                ticks='outside',
                tickfont=dict(family='Arial', size=12, color='black'),
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='black',
                linewidth=2,
                ticks='outside',
                tickfont=dict(family='Arial', size=12,color='black'),
            )
        )
        return fig

    return app

