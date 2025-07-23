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

    def prep_growth_graph(self, data):
        raw_data = pd.DataFrame(data)
        y_values = {}

        for combo in production_config.growth_current_combos:
            values = data.loc[raw_data["Combo"] == combo, production_config.growth_value_col]
            y_values[f"Combination {combo+1}"] = list(values)

        return y_values

    def gen_growth_graph(self):
        clean_data = self.reshape_growth_data()
        y_data = self.prep_growth_graph(clean_data)
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

class LorenzData:
    def __init__(self, data):
        self.dataset = pd.DataFrame(data)
        self.bins = [col for col in self.dataset.columns if col.startswith("Bin")]
        self.mid = [col for col in self.dataset.columns if col.startswith("Mid")]
    
    def split_lorenz_data(self):
        raw_data = self.dataset
        id_vars = production_config.lorenz_id_vars

#TODO: OPTIMIZE THE DATA CLEANING FOR LORENZ WITH A DEF FUNCTION

        id_data = raw_data[id_vars].copy()
        bin_cols = self.bins
        mid_cols = self.mid

        bin_prep = raw_data[bin_cols].cumsum(axis=1)
        mid_prep = raw_data[mid_cols].cumsum(axis=1)

        bin_sum = raw_data[bin_cols].sum(axis=1)
        mid_sum = raw_data[mid_cols].sum(axis=1)

        bin_prep = bin_prep.div(bin_sum, axis=0) * 100
        mid_prep = mid_prep.div(mid_sum, axis=0) * 100

        bin_data = id_data.copy()
        mid_data = id_data.copy()

        bin_data[bin_cols] = bin_prep
        mid_data[mid_cols] = mid_prep

        return mid_data, bin_data

#TODO: OBTAIN X,Y DATA FOR MULTIPLE COMBINATIONS TO PLOT THE LORENZ CURVE

    def prep_lorenz_graph(self, x_data, y_data):
        raw_x = pd.DataFrame(x_data)
        raw_y = pd.DataFrame(y_data)
        all_combos = production_config.lorenz_current_combos

        graph_data = []
        x_values, y_values = [], []

        for combo in all_combos:
            x = raw_x.loc[raw_x["Combo"] == combo, self.mid].values.flatten().tolist()
            y = raw_y.loc[raw_y["Combo"] == combo, self.bins].values.flatten().tolist()
            x_values.append(x)
            y_values.append(y)

        all_pairs = list(zip(x_values, y_values))

        i = 0
        for x, y in all_pairs:
            pair = {f"Combination {all_combos[i]}": [x, y]}
            graph_data.append(pair)
            i += 1

        return graph_data

#TODO: ADD CODE TO GRAPH THE LORENZ CURVES