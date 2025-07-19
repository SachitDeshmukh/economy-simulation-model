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