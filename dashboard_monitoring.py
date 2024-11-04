import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import mariadb
import pandas as pd

# Função para obter dados do banco de dados
def get_data_from_db(query):
    try:
        conn = mariadb.connect(
            user="monitoring_user",
            password="123456",
            host="localhost",
            database="temp_thermal_temperatures"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return pd.DataFrame(rows, columns=columns)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return pd.DataFrame()

# Função para carregar dados de temperatura
def load_temperature_data():
    query = "SELECT * FROM monitoring"
    return get_data_from_db(query)

# Função para carregar dados de consumo de CPU
def load_cpu_data():
    query = "SELECT * FROM consumption"
    return get_data_from_db(query)

# Função para criar o dashboard
def create_dashboard(df_temp, df_cpu):
    # Aplicando o tema Solar ao Dash
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
    app.title = "Dashboard de Monitoramento"

    app.layout = dbc.Container([ 
        html.H1("Dashboard de Monitoramento de Temperatura e Consumo de CPU", style={'textAlign': 'center', 'margin': '20px 0', 'color': 'white'}),

        # Contêiner para os labels (zona térmica, data, hora inicial e final)
        dbc.Row([
            dbc.Col([
                html.Label('Selecione a Zona Térmica:', style={'fontSize': 18, 'color': 'white'}),
                dcc.Dropdown(
                    id='zone-selector',
                    options=[{'label': zone, 'value': zone} for zone in df_temp.columns[2:]],
                    value=df_temp.columns[2],  # Valor padrão
                    style={'color': 'black'}
                )
            ], width=3),

            dbc.Col([
                html.Label('Data (AAAA-MM-DD):', style={'fontSize': 18, 'color': 'white'}),
                dcc.Input(
                    id='date-input',
                    type='text',
                    placeholder='AAAA-MM-DD',
                    value='2024-10-23',  # Valor padrão
                    style={'width': '100%'}
                )
            ], width=3),

            dbc.Col([
                html.Label('Hora Inicial:', style={'fontSize': 18, 'color': 'white'}),
                dcc.Input(
                    id='start-time',
                    type='text',
                    placeholder='HH:MM',
                    value='00:00',
                    style={'width': '100%'}
                )
            ], width=3),

            dbc.Col([
                html.Label('Hora Final:', style={'fontSize': 18, 'color': 'white'}),
                dcc.Input(
                    id='end-time',
                    type='text',
                    placeholder='HH:MM',
                    value='23:59',
                    style={'width': '100%'}
                )
            ], width=3)
        ], style={'padding': '20px'}),
        
        # Dropdown para selecionar múltiplos CPUs
        dbc.Row([
            dbc.Col([
                html.Label('Selecione os CPUs:', style={'fontSize': 18, 'color': 'white'}),
                dcc.Dropdown(
                    id='cpu-selector',
                    options=[{'label': f'CPU {cpu}', 'value': cpu} for cpu in df_cpu.columns[2:]],
                    multi=True,  # Permitir múltipla seleção
                    value=[df_cpu.columns[2]],  # Valor padrão (primeiro CPU)
                    style={'color': 'black'}
                )
            ], width=6)
        ], style={'padding': '20px'}),

        # Gráficos de temperaturas e consumo de CPU
        dbc.Row([
            dbc.Col([
                html.H2("Temperaturas das Zonas Térmicas", style={'textAlign': 'center'}),
                dcc.Graph(id="temperature-graph")
            ], width=6),

            dbc.Col([
                html.H2("Consumo de CPU", style={'textAlign': 'center'}),
                dcc.Graph(id="cpu-consumption-graph")
            ], width=6)
        ]),

        # Intervalo para atualização automática dos gráficos (a cada 60 segundos)
        dcc.Interval(
            id='interval-component',
            interval=60*40000,  # em milissegundos
            n_intervals=0
        ),

        # Dropdown para selecionar múltiplas zonas térmicas
        dbc.Row([
            dbc.Col([
                html.Label('Selecione as Zonas Térmicas para Visualizar:', style={'fontSize': 18, 'color': 'white'}),
                dcc.Dropdown(
                    id='multi-zone-selector',
                    options=[{'label': zone, 'value': zone} for zone in df_temp.columns[2:]],
                    multi=True,  # Permitir múltipla seleção
                    value=[df_temp.columns[2]],  # Valor padrão (primeira zona térmica)
                    style={'color': 'black'}
                )
            ], width=6)
        ], style={'padding': '20px'}),

        # Gráfico comparativo das zonas térmicas e gráfico para CPU original
        dbc.Row([
            dbc.Col([
                html.H2("Comparativo das Zonas Térmicas", style={'textAlign': 'center'}),
                dcc.Graph(id="multi-zone-temperature-graph")
            ], width=6),

            dbc.Col([
                html.H2("Consumo da CPU Original", style={'textAlign': 'center'}),
                dcc.Graph(id="original-cpu-graph")
            ], width=6)
        ])
    ], fluid=True)  # 'fluid=True' garante que o layout ocupe toda a largura da página

    # Callback para atualizar o gráfico de temperaturas
    @app.callback(
        Output('temperature-graph', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('zone-selector', 'value'),
         Input('date-input', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
    )
    def update_temperature_graph(n, selected_zone, selected_date, start_time, end_time):
        if df_temp.empty:
            return go.Figure()

        # Filtrar os dados de acordo com a data e hora
        df_filtered = df_temp[(df_temp['day'] == selected_date) & 
                              (df_temp['time'] >= start_time) & 
                              (df_temp['time'] <= end_time)]

        traces = [
            go.Scatter(
                x=df_filtered['time'], 
                y=df_filtered[selected_zone],
                mode='lines',
                name=selected_zone
            )
        ]

        return {
            'data': traces,
            'layout': go.Layout(
                title=f"Temperatura da Zona {selected_zone} no Dia {selected_date}",
                xaxis={'title': 'Hora'},
                yaxis={'title': 'Temperatura (°C)'},
                hovermode='closest'
            )
        }

    # Callback para atualizar o gráfico de consumo de CPU
    @app.callback(
        Output('cpu-consumption-graph', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('cpu-selector', 'value'),
         Input('date-input', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
    )
    def update_cpu_graph(n, selected_cpus, selected_date, start_time, end_time):
        if df_cpu.empty:
            return go.Figure()

        # Filtrar os dados de acordo com a data e hora
        df_filtered = df_cpu[(df_cpu['day'] == selected_date) & 
                             (df_cpu['time'] >= start_time) & 
                             (df_cpu['time'] <= end_time)]

        traces = []
        for cpu in selected_cpus:
            traces.append(go.Scatter(
                x=df_filtered['time'], 
                y=df_filtered[cpu],
                mode='lines',
                name=f'CPU {cpu}'
            ))

        return {
            'data': traces,
            'layout': go.Layout(
                title="Consumo de CPU ao Longo do Tempo",
                xaxis={'title': 'Hora'},
                yaxis={'title': 'Uso da CPU (%)'},
                hovermode='closest'
            )
        }

    # Callback para atualizar o gráfico comparativo das zonas térmicas
    @app.callback(
        Output('multi-zone-temperature-graph', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('multi-zone-selector', 'value'),
         Input('date-input', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
    )
    def update_multi_zone_graph(n, selected_zones, selected_date, start_time, end_time):
        if df_temp.empty:
            return go.Figure()
        # Filtrar os dados de acordo com a data e hora
        df_filtered = df_temp[(df_temp['day'] == selected_date) & 
                              (df_temp['time'] >= start_time) & 
                              (df_temp['time'] <= end_time)]

        traces = []
        for zone in selected_zones:
            traces.append(go.Scatter(
                x=df_filtered['time'], 
                y=df_filtered[zone],
                mode='lines',
                name=zone
            ))

        return {
            'data': traces,
            'layout': go.Layout(
                title="Comparativo de Temperaturas das Zonas Térmicas",
                xaxis={'title': 'Hora'},
                yaxis={'title': 'Temperatura (°C)'},
                hovermode='closest'
            )
        }

    # Callback para atualizar o gráfico da CPU original
    @app.callback(
        Output('original-cpu-graph', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-input', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
    )
    def update_original_cpu_graph(n, selected_date, start_time, end_time):
        if df_cpu.empty:
            return go.Figure()

        # Filtrar os dados de acordo com a data e hora
        df_filtered = df_cpu[(df_cpu['day'] == selected_date) & 
                             (df_cpu['time'] >= start_time) & 
                             (df_cpu['time'] <= end_time)]

        # Gráfico apenas para a CPU original
        traces = [
            go.Scatter(
                x=df_filtered['time'],
                y=df_filtered['cpu'],  # Coluna para a CPU original
                mode='lines',
                name='CPU Original'
            )
        ]

        return {
            'data': traces,
            'layout': go.Layout(
                title="Consumo da CPU Original ao Longo do Tempo",
                xaxis={'title': 'Hora'},
                yaxis={'title': 'Uso da CPU (%)'},
                hovermode='closest'
            )
        }
    
    return app 