import os
import csv
import time
import threading
from datetime import datetime
import mariadb
import sys

# Funções para obtenção de dados de zonas térmicas
def get_all_thermal_zones():
    thermal_zones = []
    for folder in os.listdir('/sys/class/thermal/'):
        if folder.startswith('thermal_zone'):
            thermal_zones.append(os.path.join('/sys/class/thermal/', folder))
    return thermal_zones

def get_all_temperatures_and_get_types(thermal_zones):
    temperatures = []
    for zone_path in thermal_zones:
        temperature = get_temperature(zone_path)
        zone_type = get_thermal_type(zone_path)
        temperatures.append((temperature, zone_type))
    return temperatures

def get_temperature(zone_path):
    with open(os.path.join(zone_path, 'temp'), 'r') as file:
        temperature = file.read().strip()
    return int(temperature) / 1000

def get_thermal_type(zone_path):
    with open(os.path.join(zone_path, 'type'), 'r') as file:
        zone_type = file.read().strip()
    return zone_type

def database_sync(table_name, record, statement):
    # Step 1: Connect to MariaDB
    print("Connecting to MariaDB!")
    try:
        conn = mariadb.connect(
            user="monitoring_user",
            password="123456",
            host="localhost",
            database="temp_thermal_temperatures"
        )
        cursor = conn.cursor()
        print("Connected to MariaDB successfully!")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # # criar o bd ja com o esquema
    '''
    if statement == "CREATE TABLE":
        print(record)
        placeholders = ', '.join(['?'] * len(record))  # Create placeholders based on number of values
        columns = []
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.execute(sql, record)
        conn.commit()
        print("New row inserted successfully!")
    '''
    
    if statement == "INSERT INTO":
        print(record)
        placeholders = ', '.join(['?'] * len(record))  # Create placeholders based on number of values
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.execute(sql, record)
        conn.commit()
        print("New row inserted successfully!")

# Função para salvar a temperatura
def save_thermal_temperature(temporary_file, permanent_file, intervalo, duracao):
    print("Starting save_thermal_temperature")
    thermal_zones = get_all_thermal_zones()
    tempo_total_execucao = duracao * 60  # Convertendo minutos para segundos
    inicio_execucao = time.time()
    
    # Verifica se o arquivo permanente já existe
    existe_arquivo_permanente = os.path.exists(permanent_file)

    with open(temporary_file, 'a', newline='') as q_temp:
        writer = csv.writer(q_temp, delimiter=';')
        
        if not existe_arquivo_permanente:  # Se o arquivo permanente não existir    
            table_name = "monitoring"
            statement = ''
            headers = ["day", "time"]
            for zone in thermal_zones:
                zone_type = get_thermal_type(zone)
                headers.append(f"{zone.split('/')[-1]} ({zone_type})")        
            writer.writerow(headers) #todo: headers aqui eh o proprio "esquema" do banco de dados. usar essa string para configurar o esquema.            
            print("headers:", headers)
            statement = "CREATE TABLE"
            database_sync(table_name, headers, statement)
            #example: database_sync(TEMP_TABLE, header, CREATE TABLE) CREATE TABLE nao vai ser usado por enquanto para evitar tentar criar a mesma tabela repetidas vezes
        while time.time() - inicio_execucao < tempo_total_execucao:
            now = datetime.now().strftime("%Y-%m-%d;%H:%M:%S")  # Modificado para separar a data e a hora
            record = [now.split(';')[0], now.split(';')[1]]  # Pegando a data e a hora separadamente
            temperatures_and_types = get_all_temperatures_and_get_types(thermal_zones)
            temperatures = [t[0] for t in temperatures_and_types]
            record.extend(temperatures)
            writer.writerow(record) ##todo: "record" eh a tupla que sera salva no BD.
            table_name = "monitoring"
            statement = "INSERT INTO"
            database_sync(table_name, record, statement)
            time.sleep(intervalo * 60)

    with open(temporary_file, 'r') as temp_file, open(permanent_file, 'a', newline='') as perm_file:
        perm_file.write(temp_file.read())

    # Apaga os dados do arquivo temporário
    with open(temporary_file, 'w'):
        pass

    print("Coleta de temperaturas finalizadas.")

# Funções para obtenção de dados de uso de CPU
def read_cpu_usage():
    cpu_stats = {}
    with open('/proc/stat', 'r') as f:
        for line in f:
            if line.startswith('cpu'):
                fields = line.split()
                if len(fields) < 8:
                    continue
                cpu_id = fields[0]
                user, nice, system, idle, iowait, irq, softirq, steal = map(int, fields[1:9])
                total_time = user + nice + system + idle + iowait + irq + softirq + steal
                idle_time = idle + iowait
                cpu_stats[cpu_id] = (total_time, idle_time)
    return cpu_stats

def calculate_cpu_usage(old_stats, new_stats):
    cpu_usage = {}
    for cpu in old_stats:
        old_total, old_idle = old_stats[cpu]
        new_total, new_idle = new_stats[cpu]
        total_diff = new_total - old_total
        idle_diff = new_idle - old_idle
        if total_diff == 0:
            usage = 0
        else:
            usage = 100 * (total_diff - idle_diff) / total_diff
        cpu_usage[cpu] = usage
    return cpu_usage

# Função para salvar o uso de CPU
def save_consumption(temporary_file, permanent_file, intervalo, duracao):
    print("Starting save_consumption")
    tempo_total_execucao = duracao * 60  # Convertendo minutos para segundos
    inicio_execucao = time.time()

    existe_arquivo_permanente = os.path.exists(permanent_file)
    cpu_label_list = read_cpu_usage()
    cpu_label_list = list(cpu_label_list.keys())
    print(cpu_label_list)

    with open(temporary_file, 'a', newline='') as q_temp:
        writer = csv.writer(q_temp, delimiter=';')
        if not existe_arquivo_permanente:
            headers = ["day", "time"]
            for cpu in cpu_label_list:
                headers.append(cpu)
            writer.writerow(headers)

        old_stats = read_cpu_usage()
        

        while time.time() - inicio_execucao < tempo_total_execucao:
            now = datetime.now().strftime("%Y-%m-%d;%H:%M:%S")
            record = [now.split(';')[0], now.split(';')[1]]
            new_stats = read_cpu_usage()
            cpu_consumption = calculate_cpu_usage(old_stats, new_stats)
            record.extend(list(cpu_consumption.values()))
            
            # Escreve os dados no arquivo temporário
            writer.writerow(record)
            
            # Inserindo os dados no banco de dados
            table_name = "consumption" 
            statement = "INSERT INTO"
            database_sync(table_name, record, statement)  # Sincronizando com o banco de dados
            
            old_stats = new_stats
            time.sleep(intervalo * 60)

    with open(temporary_file, 'r') as temp_file, open(permanent_file, 'a', newline='') as perm_file:
        perm_file.write(temp_file.read())

    with open(temporary_file, 'w'):
        pass

    print("Coleta de recursos de processamento e memoria finalizadas.")

# Função principal para iniciar a coleta
def start_collection(duration, interval):
    print("start_collection routine started")
    thermal_temporary_file = 'temp_temporarias.csv'
    thermal_permanent_file = 'permanente_temperature_collection.csv'
    consumption_temporary_file = 'consumption_temporary_file.csv'
    consumption_permanent_file = 'consumption_permanent_file.csv'
    
        # Barreira para sincronizar as duas threads
    barrier = threading.Barrier(2)  # Sincroniza duas threads
    
    # Função que envolve save_thermal_temperature para sincronizar com barrier
    def thermal_thread():
        save_thermal_temperature(thermal_temporary_file, thermal_permanent_file, interval, duration)
        barrier.wait()  # Aguarda a outra thread
    
    # Função que envolve save_consumption para sincronizar com barrier
    def consumption_thread():
        save_consumption(consumption_temporary_file, consumption_permanent_file, interval, duration)
        barrier.wait()  # Aguarda a outra thread
    
    # Inicia as threads para salvar a temperatura e o consumo
    thread1 = threading.Thread(target=thermal_thread)
    thread2 = threading.Thread(target=consumption_thread)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()  
    #save_thermal_temperature (thermal_temporary_file, thermal_permanent_file, interval, duration)

    #thread1 = threading.Thread(target=save_thermal_temperature, args=(thermal_temporary_file, thermal_permanent_file, interval, duration))
    #thread2 = threading.Thread(target=save_consumption, args=(consumption_temporary_file, consumption_permanent_file, interval, duration))
    
    #thread1.start()
    #thread2.start()
    
    #thread1.join()
    #thread2.join()

def read_parameters():
    while True:
        try:
            duration = int(input("Please enter the duration in minutes: "))
            if duration <= 0:
                print("Duration must be a positive integer. Please try again.")
                continue
            interval = int(input("Please enter the interval in minutes: "))
            if interval <= 0:
                print("Interval must be a positive integer. Please try again.")
                continue
            elif interval > duration:
                print("Interval must be less than or equal to the duration. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    return duration, interval

def main():
    duration, interval = read_parameters()
    start_collection(duration, interval)

if __name__ == "__main__":
    main()


