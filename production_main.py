import logging  # Logging setup for monitoring execution
import msvcrt # To work with keyboard input

# Set logging format and level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Importing the modules
import production_simulation
import production_graph
import production_config

def ask_yes_no_keypress(prompt):
    print(prompt, end='', flush=True)
    while True:
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 'y':
            print('Y')
            return True
        elif key == 'n':
            print('N')
            return False

def main():
    SIM_DONE = ask_yes_no_keypress("Is the simulation already complete? [Y/N]: ") # user to define before each simulation
    GEN_GRAPH = ask_yes_no_keypress("Do you want to generate the graphs? [Y/N]: ") # user to define before each simulation

    while GEN_GRAPH:
        if not SIM_DONE:
            results = production_simulation.simulate() # simulate the NETLOGO model if not simulated before
            SIM_DONE = True
        else:
            results = production_graph.load_data() # load pre-existing data from Excel sheet
        if production_config.current_opt == "opt_1":
            Graph = production_graph.GrowthData(results)
            Graph.gen_growth_graph()
        elif production_config.current_opt == "opt_2":
            pass
        elif production_config.current_opt == "opt_3":
            pass
        else:
            pass
        GEN_GRAPH = False
    else:
        if not SIM_DONE:
            production_simulation.simulate()
            logging.info("The graphs were not generated.")

if __name__ == "__main__":
    main() # THIS IS THE MAIN PYTHON FILE FOR THE PRODUCTION MODEL