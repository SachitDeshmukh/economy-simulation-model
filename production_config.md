
# TEMPLATE TO SET UP CONFIGURATION SETTING

This file contains the **configuration settings for the python code** files to run. The configuration settings are stored in variables and the file is imported as a python module in the respective python files to access the values in the variables.

    # Defining all the globals for the territory model

## SET UP ALL THE PATHS FOR THE WORKING DIRECTORY

    # PATHS
    main_dir = r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\Economy-model-Ishwari-2025"
    netlogo_exe = r"C:\Users\Sachit Deshmukh\AppData\Local\NetLogo"
    model = r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\Economy-model-Ishwari-2025\Ishwari-private-property.nlogo"

## DEFINE THE COMBINATIONS FOR THE INPUT PARAMETERS

    # INPUT VALUES
    input_parameters = {
                "num-workers": [50], # 1
                "num-owners": [50], # 1
                "num-assets": [25, 50, 75], # 3
            }

    percent_parameters = [(30, 50, 20), (80, 10, 10), (10, 45, 45), (20, 75, 5)] # 4
    percent_keys = ("percent-capital", "percent-wages", "percent-owner-income")

## DEFINE THE VALUES RELEVENT TO GERENATE THE DATA

    # DATA PARTICULARS
    file_name = "NETLOGO_production"

    # SIMULATION SET UP
    parallel_jobs = 6
    max_ticks = 100
    runs = 300

    lorenz_bins = int(20)
    lorenz_id_prep = ["Combo", "Run", "Workers", "Owners", "Assets", "Capital_perc", "Wages_perc", "Income_perc"]
    lorenz_var_prep = "Agent Serial"
    lorenz_value_prep = "Wealth"
    lorenz_column_suffix_prep = "_wealth"

    backup_g_raw = "Growth_output_raw"
    backup_g_clean = "Growth_output_clean"
    backup_l_raw = "Lorenz_output_raw"
    backup_l_clean = "Lorenz_output_clean"
    backup_i_raw = "Gini_output_raw"
    backup_i_clean = "Gini_output_clean"

    data_particulars = {"opt_1": {"GROWTH": {"RAW": backup_g_raw, "CLEAN": backup_g_clean}},
                        "opt_2": {"LORENZ": {"RAW": backup_l_raw, "CLEAN": backup_l_clean}},
                        "opt_3": {"GINI": {"RAW": backup_i_raw, "CLEAN": backup_i_clean}}
                        }
    data_options = list(data_particulars) # ["opt_1", "opt_2", "opt_3"]
    current_opt = data_options[1] # "opt_2"

## DEFINE THE VALUES RELEVENT TO GERENATE THE GRAPHS

    # GRAPHS
    ## Growth
    growth_id_vars = ["Combo", "Workers", "Owners", "Assets", "Capital_perc", "Wages_perc", "Income_perc"]
    growth_var_col = "Tick Count"
    growth_value_col = "Avg Growth Perc"
    growth_column_prefix = "Avg-growth-rate_"
    growth_current_combos = [0, 1, 2, 3, 4]
    growth_X_data = [x for x in range(max_ticks+1)]
    growth_X_label = "Tick count"
    growth_Y_label = "Average growth rate at tick"
    growth_graph_title = "Average Growth Rate of Economy's Wealth"

    ## Lorenz
    lorenz_id_vars = ["Combo", "Workers", "Owners", "Assets", "Capital_perc", "Wages_perc", "Income_perc"]
    lorenz_var_col = "Temp_Category"
    lorenz_value_col = "Temp_Data"
    lorenz_current_combos = [4, 5, 6, 7] # list(range(1, 12, 3))
    lorenz_X_label = "Percentage of people in the economy"
    lorenz_Y_label = "Percentage of wealth in the economy"
    lorenz_graph_title = "Lorenz Curve of the Economy's Wealth"

    true_equality_x = list(range(0, 101, int(100/lorenz_bins)))
    true_equality_y = true_equality_x
