import pandas as pd
import thermal_zone_monitoring
import dashboard_monitoring
import teste_dash_monitoring
from thermal_zone_monitoring import main, get_all_thermal_zones, get_all_temperatures, get_temperature, save_thermal_temperature
from dashboard_monitoring import main, load_temperature_data, plot_interval_temperature
from thermal_zone_monitoring import main as thermal_zone_main
from teste_dash_monitoring import load_temperature_data, dashboard
import sys
import subprocess

def main_function_1():
    print("Main function 1 is executing")
    # Your code for the first main function goes here

def main_function_2():
    print("Main function 2 is executing")
    # Your code for the second main function goes here
#
def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "1":
            print("Monitoring will run in the background")
            process = subprocess.Popen(['python3', 'thermal_zone_monitoring.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif arg == "2":
            print("Monitoring will run in the current window")
            thermal_zone_monitoring.main()
        elif arg == "3":
            print("Comsuption monitoring will run in the background")
            process = subprocess.Popen(['python3', 'consumption_monitoring.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif arg == "4":
            print("Comsuption monitoring will run in the current window")
            #consumption_monitoring.main()
        elif arg == "5":
            print("Dashboard monitoring will run in the current window")
            dashboard_monitoring.main()
        elif arg == "6":
            print("Dashboard monitoring will run in the current window")
            def main(file_path):
                df = load_temperature_data(file_path)
                app = dashboard(df)
                app.run_server(debug=True)

            if __name__ == '__main__':
                file_path = "historico_permanente_coletas_temperaturas.csv" 
                main(file_path)
        else:
            print("Invalid argument. Use '1, 2, 3, 4, 5 or 6' to choose a function.")
    else:
        print("Usage: python script.py [1|2]")

if __name__ == "__main__":
    main()