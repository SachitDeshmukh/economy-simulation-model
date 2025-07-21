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
def gen_param_combos(agent_params, perc_params):
    first_keys = tuple(agent_params.keys())
    add_keys = production_config.percent_keys
    new_keys = first_keys + add_keys
    first_values = [values for values in product(*agent_params.values())]
    add_values = perc_params

    new_values = []
    for og_param in first_values:
        for add_param in add_values:
            new_param = og_param + add_param
            new_values.append(new_param)

    all_combos = [dict(zip(new_keys, values)) for values in new_values]
    return all_combos

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

        growth_data, lorenz_data = [], []

        try:
            for param, value in combo.items():
                netlogo.command(f"set {param} {value}")  # Set model parameters from combo

            for i in range(total_runs):
                netlogo.command("setup")  # Initialize simulation

                common_id = {
                    "Combo": combo_serial,
                    "Run": i+1,
                    "Workers": combo.get("num-workers"),
                    "Owners": combo.get("num-owners"),
                    "Assets": combo.get("num-assets"),
                    "Capital_perc": combo.get("percent-capital"),
                    "Wages_perc": combo.get("percent-wages"),
                    "Income_perc": combo.get("percent-owner-income")
                    }
                growth_addon, lorenz_addon = {}, {}

                current_tick = int(netlogo.report("ticks"))

                while current_tick < self.target_ticks:
                    netlogo.command("go")
                    growth_addon[f"Growth-rate_{current_tick}"] = netlogo.report("pt-growth-rate")
                    current_tick = int(netlogo.report("ticks"))
                worker_wealths = netlogo.report("[wealth] of workers")
                owner_wealths = netlogo.report("[wealth] of owners")
                agents = {"worker": worker_wealths, "owner": owner_wealths} 
                for agent, data in agents.items():
                    for j in range(len(data)):
                        lorenz_addon[f"{agent}_{j}_wealth"] = data[j]

                growth_combined = {**common_id, **growth_addon}
                lorenz_combined = {**common_id, **lorenz_addon}

                growth_data.append(growth_combined)
                lorenz_data.append(lorenz_combined)

                logging.info(f"Combination {combo_serial} iteration {i+1} complete.")

        except Exception as e:
            logging.error(f"Simulation error with params {combo}: {e}")
            return [], []  # Ensure failed runs don’t corrupt output

        finally:
            netlogo.kill_workspace()  # Close NetLogo workspace
            time.sleep(0.2)

        return growth_data, lorenz_data
    
    # Prepare Growth data
    def prep_growth(self, data):
        data = pd.DataFrame(data)
        for i in range(self.target_ticks):
            avg_growth_rate = data.groupby("Combo")[f"Growth-rate_{i}"].mean().reset_index()
            avg_growth_rate.rename(columns={f"Growth-rate_{i}": f"Avg-growth-rate_{i}"}, inplace=True)
            data = data.merge(avg_growth_rate, on="Combo")
        return data
    
    def prep_lorenz(self, data):
        data = pd.DataFrame(data)
        return data

    def prep_gini(self, data):
        data = pd.DataFrame(data)
        return data

    # PREPARE ALL DATA FOR ANALYSIS
    def prep_data(self, results, option):
        results_data = pd.DataFrame(results)
        if option == production_config.data_options[0]:
            prep_data = self.prep_growth(results_data)
            return prep_data
        elif option == production_config.data_options[1]:
            prep_data = self.prep_lorenz(results_data)
            return prep_data
        elif option == production_config.data_options[2]:
            prep_data = self.prep_gini(results_data)
            return prep_data
        else:
            return pd.DataFrame()

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
        param_combinations = gen_param_combos(production_config.input_parameters, production_config.percent_parameters)
        start_time_temp = datetime.now()
        simulation = NetLogoSim(param_combinations, runs=production_config.runs, ticks=production_config.max_ticks)  # Initialize simulation object
        results = Parallel(n_jobs=production_config.parallel_jobs, backend="multiprocessing")(
            delayed(simulation.netlogo_model)(combo) for combo in simulation.params)
        results = [res for res in results if res[0] or res[1]]
        growth_raw = [entry for res in results for entry in res[0] if entry]
        lorenz_raw = [entry for res in results for entry in res[1] if entry]
        end_time_temp = datetime.now()
        total_time = (end_time_temp - start_time_temp).total_seconds()
        logging.info(f"Time taken: {total_time}.")

    finally:
        logging.info("CLEANING UP RESOURCES...")
        jpype.shutdownJVM()  # Shut down Java Virtual Machine

    logging.info("ALL SIMULATIONS COMPLETE.")

    growth_results, lorenz_results = simulation.prep_data(growth_raw, production_config.data_options[0]), simulation.prep_data(lorenz_raw, production_config.data_options[1])
    save_data(growth_results, backup_file_name=f"{production_config.backup_g_raw}", sheet_prefix="G_RAW")
    save_data(lorenz_results, backup_file_name=f"{production_config.backup_l_raw}", sheet_prefix="L_RAW")

    clean_growth = simulation.drop_duplicates(growth_results)
    save_data(clean_growth, backup_file_name=f"{production_config.backup_g_clean}", sheet_prefix="G_CLEAN")

    data_sets = {production_config.data_options[0]: clean_growth, production_config.data_options[1]: lorenz_results, production_config.data_options[2]: pd.DataFrame()}
    return_data = data_sets[f"{production_config.current_opt}"]
    return return_data # THIS IS THE NETLOGO SIMULATION PYTHON FILE FOR THE PRODUCTION MODEL