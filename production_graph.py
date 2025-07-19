# THIS IS THE DATA ANALYSIS PYTHON FILE FOR THE PRODUCTION MODEL
import os  # Importing OS module for file operations
import pandas as pd  # Import Pandas for data processing
import numpy as np # Import Numpy
import matplotlib.pyplot as plt  # Plotting graphs with Matplotlib
import logging  # Logging setup for monitoring execution
import production_config # Importing the simulation module
from datetime import datetime  # Date/time handling utilities

def load_data():
    while True:
        file_input = input("Please enter the name of Excel file with the data: ")
        if os.path.exists(os.path.join(production_config.main_dir, file_input)) == False:
            print("This file name is incorrect.")
            continue
        else:
            source_file = pd.ExcelFile(file_input)
            break

    while True:
        source_sheet = input("Please enter the name of Excel sheet with the data: ")
        if not source_sheet in source_file.sheet_names:
            print("This sheet name is incorrect.")
            continue
        else:
            results = pd.read_excel(source_file, sheet_name=source_sheet)
            logging.info("Successfully loaded data.")
            break
    return results

class GrowthData:
    def __init__(self, data):
        self.dataset = pd.DataFrame(data)

    def reshape_growth_data(self):
        raw_data = self.dataset
        id_vars = production_config.growth_id_vars
        melt_cols = [col for col in raw_data.columns if col.startswith(production_config.growth_column_prefix)]
        var_name = production_config.growth_var_col
        value_name = production_config.growth_value_col

        reshape_data = pd.melt(raw_data, id_vars=id_vars, value_vars=melt_cols, var_name=var_name, value_name=value_name, ignore_index=False)
        reshape_data[var_name] = reshape_data[var_name].str.replace(production_config.growth_column_prefix, "", regex=False)
        return reshape_data

    def prep_graph_data(self, data):
        raw_data = pd.DataFrame(data)
        y_values = {}

        for combo in production_config.growth_current_combos:
            values = data.loc[raw_data["Combo"] == combo, production_config.growth_value_col]
            y_values[f"Combination {combo+1}"] = list(values)

        return y_values

    def gen_growth_graph(self):
        clean_data = self.reshape_growth_data()
        y_data = self.prep_graph_data(clean_data)
        x_data = production_config.growth_X_data

        plt.figure(figsize=(12, 6))
        for label, y_combo in y_data.items():
            plt.plot(x_data, y_combo, label=label)
        plt.xlabel(production_config.growth_X_label)
        plt.ylabel(production_config.growth_Y_label)
        plt.legend()
        plt.title(production_config.growth_graph_title)

        png_file = f"{production_config.file_name}_{list(production_config.data_particulars[production_config.current_opt].keys())[0]}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        plt.savefig(png_file, dpi=300, bbox_inches='tight')

        logging.info(f"GRAPH GENERATED. FILE SAVED TO {png_file}")