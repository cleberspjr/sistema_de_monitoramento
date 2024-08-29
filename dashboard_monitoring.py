import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_temperature_data(file_path):
    return pd.read_csv(file_path, delimiter=';')

def load_cpu_data(file_path):
    return pd.read_csv(file_path, delimiter=';')

def send_email_alert(temperature, time, zone):
    sender_email = "fulano.email"
    receiver_email = "siclano.email"
    password = "sua_senha"

    subject = "Alerta de Temperatura Excedente"
    body = f"A temperatura na zona {zone} excedeu o limite! \n\n" \
           f"Temperatura: {temperature} C°\n" \
           f"Horário: {time}\n"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "ALERTA DE TEMPERATURA EXCEDIDA"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Substitua pelo seu servidor SMTP
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("E-mail de alerta enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


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
        limite_temperatura = 60
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

        # Adicionando a linha horizontal no gráfico para indicar o limite máximo de temperatura
        fig.add_hline(y=limite_temperatura, line_dash="dash", line_color="red", annotation_text="Limite Máximo", 
                      annotation_position="top right")

        alert_msg = ""
        if df_filtered[selected_zone].max() > limite_temperatura:
            alert_msg = f"ALERTA: A temperatura na zona térmica {selected_zone} excedeu o limite!"

            # Encontra o tempo exato em que a temperatura excedeu o limite
            tempo_excedeu = df_filtered[df_filtered[selected_zone] > limite_temperatura]['time'].iloc[0]
            temperatura_excedeu = df_filtered[df_filtered[selected_zone] > limite_temperatura][selected_zone].iloc[0]

            send_email_alert(temperatura_excedeu, tempo_excedeu, selected_zone)

            # Adiciona uma anotação no gráfico onde a temperatura excedeu o limite
            fig.add_annotation(
                x=tempo_excedeu,
                y=temperatura_excedeu,
                text="Excedeu limite!",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(color="red", size=12, family="Arial"),
                bgcolor="rgba(255,255,255,0.6)"
            )

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

