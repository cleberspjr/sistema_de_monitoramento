import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

def load_temperature_data(file_path):
    return pd.read_csv(file_path, delimiter=';')

def dashboard(df):
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
                    options=[{'label': col, 'value': col} for col in df.columns if 'zone' in col],
                    value=df.columns[2],  #zona padrão
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
            dbc.Col(dcc.Graph(id='temperature-graph', style={'backgroundColor': '#f8f9fa'}), width=12)  # Cor do contêiner do gráfico
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='alert-message', style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}), width=12)
        ])
    ], fluid=True)

    @app.callback(
        [Output('temperature-graph', 'figure'),
         Output('alert-message', 'children')],
        [Input('zone-dropdown', 'value'),
         Input('initial-time', 'value'),
         Input('final-time', 'value'),
         Input('day', 'value')]
    )
    def graphic(selected_zone, initial_time_interval, final_time_interval, day):
        limite_temperatura = 75
        df_filtered = df[(df['day'] == day) & (df['time'] >= initial_time_interval) & (df['time'] <= final_time_interval)]

        fig = px.line(df_filtered, x='time', y=selected_zone, title=f'Temperatura na {selected_zone} na data {day}')
        fig.update_layout(
            xaxis_title='Horario do dia',
            yaxis_title='Temperatura em C°',
            plot_bgcolor='rgba(0,0,0,0)',  # Cor do plano de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Cor do plano de fundo do papel
            font=dict(color='black'),  # Cor do texto
            title_font=dict(size=20, color='black', family='Arial'),
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='black',
                linewidth=2,
                ticks='outside',
                tickfont=dict(family='Arial', size=12, color='black',
                ),
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
        # Verifica se a temperatura excede o limite
        if df_filtered[selected_zone].max() > limite_temperatura:
            alert_msg = f"ALERTA: A temperatura na zona térmica {selected_zone} excedeu o limite!"

        return fig, alert_msg

    return app