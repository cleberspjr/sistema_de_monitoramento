import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime
import schedule
import time
import os
import re
import subprocess
import pandas as pd
from pathlib import Path
import time
import threading

def load_temperature_data():
    file_path = "historico_permanente_coletas_temperaturas.csv"
    return pd.read_csv(file_path, delimiter=';')

def plot_interval_temperature(dataframe, zone, initial_time_interval, final_time_interval, day, limite_temperatura):
    df_filtered = dataframe[(dataframe['day'] == day) & (dataframe['time'] >= initial_time_interval) & (dataframe['time'] <= final_time_interval)]

    plt.figure(figsize=(10, 6))

    for column in df_filtered.columns:
        if zone in column:
            plt.plot(df_filtered['time'], df_filtered[column], label=column)

            # Verifica se a temperatura excede o limite
            if df_filtered[column].max() > limite_temperatura:
                # Envia um print na tela avisando o problema
                print(f"ALERTA: A temperatura na zona térmica {column} excedeu o limite!")
                alert_msg = "Temperatura acima do limite"
                plt.text(0.98, 0.98, alert_msg, transform=plt.gca().transAxes, fontsize=12, color='white',
                         ha='right', va='top', bbox=dict(facecolor='red', edgecolor='red', pad=8))


    plt.title(f"Temperature for {day}")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend(loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def save_info_proc_file(name_file ='info_proc.txt'):
    informacoes = {}
    
    with open('/proc/cpuinfo', 'r') as file:
        linhas = file.readlines()

    for linha in linhas:
        # Separa a linha em chave e valor
        partes = linha.strip().split(':')
        if len(partes) == 2:
            chave = partes[0].strip()
            valor = partes[1].strip()
            informacoes[chave] = valor

    with open("output/name_file", 'w') as file:
        for chave, valor in informacoes.items():
            file.write(f'{chave}: {valor}\n')

    print(f'Informações do processador salvas em {name_file}')


def print_several_temps_all_zones(file):
    df = pd.read_csv(file, sep=";", header=None)
    
    time_list = df[df.columns[1]].values.tolist()[1:]
    zones_dict = {}    
    all_zones_in_a_dictionary(zones_dict, df)
    print(zones_dict)
    zonesdict = zones_dict
    
    df = pd.DataFrame(data=zonesdict)
    df.index = time_list
    df.plot.line(figsize=(10, 6))
    plt.title("Temperaturas em todas as zonas")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
#funcao nova
def all_zones_in_a_dictionary(zones_dict, df):

    for i in range(2, df.shape[1]):
        print("accessing position:", i)
        zone_name = df[df.columns[i]].values.tolist()[0]
        temp_list = df[df.columns[i]].values.tolist()[1:]
        temp_list_2 = [float(element) for element in temp_list]

        zones_dict[str(zone_name)] = temp_list_2
    return zones_dict

def main():


    #print("Here you will ask for the user's inputs and call all dashboard functions")

    df = load_temperature_data()

    zone = input("Digite a zona térmica desejada: ")
    initial_time_interval = input("Digite o tempo inicial (HH:MM): ")
    final_time_interval = input("Digite o tempo final (HH:MM): ")
    day = input("Digite o dia que deseja plotar (YYYY-MM-DD): ")
    limite_temperatura = 75

    plot_interval_temperature(df, zone, initial_time_interval, final_time_interval, day, limite_temperatura)

 
