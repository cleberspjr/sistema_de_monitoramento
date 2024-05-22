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
import csv

def get_all_thermal_zones():
    thermal_zones = []
    for folder in os.listdir('/sys/class/thermal/'):
        if folder.startswith('thermal_zone'):
            thermal_zones.append(os.path.join('/sys/class/thermal/', folder))
    return thermal_zones

def get_all_temperatures(thermal_zones):
    temperatures = []
    for zone_path in thermal_zones:
        temperature = get_temperature(zone_path)
        temperatures.append(temperature)
    return temperatures

def get_temperature(zone_path):
    with open(os.path.join(zone_path, 'temp'), 'r') as file:
        temperature = file.read().strip()
    return int(temperature) / 1000

#Parameters:
# intevalo: How many minutes of interval between each collect
# duracao: The duration of the query (in minutes)
# todo: duracao cannot be less than intevalo
def save_thermal_temperature(temporary_file, permanent_file, intervalo, duracao):
    thermal_zones = get_all_thermal_zones()
    tempo_total_execucao = duracao * 60  # Convertendo minutos para segundos
    inicio_execucao = time.time()
   
    # Verifica se o arquivo permanente já existe
    existe_arquivo_permanente = os.path.exists(permanent_file)

    with open(temporary_file, 'a', newline='') as q_temp:
        writer = csv.writer(q_temp, delimiter=';')
        if not existe_arquivo_permanente:  # Se o arquivo permanente não existir
            label = ["day", "time"] + [zone.split('/')[-1] for zone in thermal_zones]
            writer.writerow(label)

        while time.time() - inicio_execucao < tempo_total_execucao:
            now = datetime.now().strftime("%Y-%m-%d;%H:%M:%S")  # Modificado para separar a data e a hora
            record = [now.split(';')[0], now.split(';')[1]]  # Pegando a data e a hora separadamente
            temperatures = get_all_temperatures(thermal_zones)
            record.extend(temperatures)
            writer.writerow(record)
            time.sleep(intervalo * 60)

    with open(temporary_file, 'r') as temp_file, open(permanent_file, 'a', newline='') as perm_file:
        perm_file.write(temp_file.read())

    # Apaga os dados do arquivo temporário
    with open(temporary_file, 'w'):
        pass

    print("Coleta de temperaturas finalizadas.")



def background_collect():

    temporary_file = 'temperaturas_temporarias.csv'
    permanent_file = 'historico_permanente_coletas_temperaturas.csv'
    save_thermal_temperature(temporary_file, permanent_file, 1, 5)  # Coleta temperatura de todas as zonas térmicas a cada 1 minuto por 2 minutos
    print("Thread 1")

def background_collect_menu():
    print("A monitoring collection started... do not close this window")
    print("Real time  text information will be displayed here in the future")


def main():    
    output_file_unico = "temp_database.csv"
    output_file_varios = "temp_database_all.csv" 
    output_file_varios_teste = "temp_database_all.csv" 
    output_processor_info = "processor_info.csv"
    #Especifica a zona termal que se quer medir    
    
    # Exemplo de uso
    print("starting monitoring in background")    

    # Salvar as informacoes do processador
    thread1 = threading.Thread(target=background_collect, args=())    
    thread1.start()
    thread2 = threading.Thread(target=background_collect_menu, args=())    
    thread2.start()
    
