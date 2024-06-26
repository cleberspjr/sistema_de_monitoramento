import sys
import thermal_zone_monitoring
import dashboard_monitoring
from thermal_zone_monitoring import main as thermal_zone_main
from dashboard_monitoring import load_temperature_data, dashboard

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "1":
            print("Monitoring will run in the current window")
            thermal_zone_monitoring.main() 

        elif arg == "6":    
            print("Dashboard monitoring will run in the current window")
            run_dashboard()

        else:
            print("Invalid argument. Use '1 or 6' to choose a function.")
    else:
        print("Usage: python script.py [1|6]")

def run_dashboard():
    df_temp = load_temperature_data("permanente_temperature_collection.csv")
    df_cpu = load_temperature_data("consumption_permanent_file.csv")
    app = dashboard(df_temp, df_cpu)
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
