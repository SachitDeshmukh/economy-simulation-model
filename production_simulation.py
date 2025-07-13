import os  # Importing OS module for file operations
import pandas as pd  # Import Pandas for data processing
import logging  # Logging setup for monitoring execution
import time  # Time module for delays
import jpype  # Interface for Java-Python interactions
from datetime import datetime  # Date/time handling utilities
from itertools import product, chain  # Cartesian product for param combinations
from joblib import Parallel, delayed  # Parallel execution for simulations
from pynetlogo import NetLogoLink  # Interface for NetLogo simulations

import production_config # To import all GLOBALS

# Generate all possible parameter combinations
def gen_param_combos(all_params):
    return [dict(zip(all_params.keys(), values)) for values in product(*all_params.values())]

# Save simulation data in CSV and Excel formats
def save_data(data, backup_file_name, sheet_prefix):
    data.to_csv(f"{backup_file_name}.csv")

    xlsx_file_name = f"{production_config.file_name}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    mode = 'a' if os.path.exists(xlsx_file_name) else 'w'
    with pd.ExcelWriter(xlsx_file_name, mode=mode, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name=f"{sheet_prefix}_{datetime.now().strftime("%H-%M-%S")}", index=False)

    logging.info(f"RESULTED SAVED TO {xlsx_file_name}")

# NetLogo simulation class handling execution
class NetLogoSim:
    def __init__(self, parameters, runs, ticks):
        self.params = parameters  # Store parameter combinations
        self.runs = runs  # Define the number of simulation runs
        self.target_ticks = int(ticks + 1) # to account for python's limitation with range()

    # Run simulation for a parameter combination
    def netlogo_model(self, combo):
        netlogo = NetLogoLink(gui=False, netlogo_home=production_config.netlogo_exe)
        netlogo.load_model(production_config.model)

        combo_serial = self.params.index(combo)
        total_runs = self.runs
        capital, wages, incomce = production_config.capital, production_config.wages, production_config.owner_income

        all_results = []

        try:
            for param, value in combo.items():
                netlogo.command(f"set {param} {value}")  # Set model parameters from combo
                netlogo.command(f"set percent-capital {capital}")
                netlogo.command(f"set percent-wages {wages}")
                netlogo.command(f"set percent-owner-income {incomce}")

            for i in range(total_runs):
                netlogo.command("setup")  # Initialize simulation

                results = {
                    "Combo": combo_serial,
                    "Run": i+1,
                    "Workers": combo.get("num-workers"),
                    "Owners": combo.get("num-owners"),
                    "Assets": combo.get("num-assets"),
                    "Capital_perc": capital,
                    "Wages_perc": wages,
                    "Income_perc": incomce
                    }

                current_tick = int(netlogo.report("ticks"))

                while current_tick < self.target_ticks:
                    netlogo.command("go")
                    results[f"Growth-rate_{current_tick}"] = netlogo.report("pt-growth-rate")
                    current_tick = int(netlogo.report("ticks"))
                
                all_results.append(results)
                logging.info(f"Combination {combo_serial} iteration {i+1} complete.")
      
        except Exception as e:
            logging.error(f"Simulation error with params {combo}: {e}")
            return None  # Ensure failed runs don’t corrupt output
        
        finally:
            netlogo.kill_workspace()  # Close NetLogo workspace
            time.sleep(0.2)

        return all_results

    # Filter valid results and compute averages
    def filter_params(self, results):
        results = [res for res in results if res is not None]
        result_data = pd.DataFrame(results)
        # result_data.to_csv(f"test_output_16-38.csv")
        for i in range(self.target_ticks):
            avg_growth_rate = result_data.groupby("Combo")[f"Growth-rate_{i}"].mean().reset_index()
            avg_growth_rate.rename(columns={f"Growth-rate_{i}": f"Avg-growth-rate_{i}"}, inplace=True)
            result_data = result_data.merge(avg_growth_rate, on="Combo")         
        return result_data
    
    def drop_duplicates(self, dataset):
        dataset = pd.DataFrame(dataset)
        unique_id = ["Combo", "Workers", "Owners", "Assets", "Capital_perc", "Wages_perc", "Income_perc"]
        dataset = dataset.drop_duplicates(subset=unique_id)
        clean_data = dataset[unique_id].copy()
        for i in range(self.target_ticks):
            clean_data[f"Avg-growth-rate_{i}"] = dataset[f"Avg-growth-rate_{i}"]
        return clean_data

# Main execution function
def simulate():
    os.chdir(production_config.main_dir)  # Change working directory to main directory

    if not jpype.isJVMStarted():
        jpype.startJVM()  # Start Java Virtual Machine

    try:
        logging.info(f"Starting iteration...")
        param_combinations = gen_param_combos(production_config.input_parameters)
        start_time_temp = datetime.now()
        simulation = NetLogoSim(param_combinations, runs=production_config.runs, ticks=production_config.max_ticks)  # Initialize simulation object
        iter_data_nested = Parallel(n_jobs=production_config.parallel_jobs, backend="multiprocessing")(
            delayed(simulation.netlogo_model)(combo) for combo in simulation.params) # Run simulations in parallel
        iter_data = list(chain.from_iterable(filter(None, iter_data_nested)))
        end_time_temp = datetime.now()
        total_time = (end_time_temp - start_time_temp).total_seconds()
        logging.info(f"Time taken: {total_time}.")

    finally:
        logging.info("CLEANING UP RESOURCES...")
        jpype.shutdownJVM()  # Shut down Java Virtual Machine

    logging.info("ALL SIMULATIONS COMPLETE.")

    production_results = simulation.filter_params(iter_data)
    save_data(production_results, backup_file_name=f"{production_config.backup_raw}", sheet_prefix="RAW")

    clean_results = simulation.drop_duplicates(production_results)
    save_data(clean_results, backup_file_name=f"{production_config.backup_clean}", sheet_prefix="CLEAN")

    return clean_results # THIS IS THE NETLOGO SIMULATION PYTHON FILE FOR THE PRODUCTION MODEL