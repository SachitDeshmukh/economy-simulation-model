
# AGENT-BASED ECONOMY MODEL TO STUDY ECONOMIC INEQUALITY

In this model, [Ishwari](https://github.com/social-stimulator) studies the phenomenon of income distribution and economic inequality in a system. This includes the ownership of assets, determination of wages, and hierarchy in economic systems. It is a **NETLOGO model** of production which analyses the dynamics of land, labour and capital - three essential factors for economic production.

## WHAT IS THE MODEL ABOUT?

> The model has **three agent types**.

1. The firrst agent type is **workers**.
2. The second agent type is **owners**.
3. The third agent type is **assets**.

##  HOW DOES THE MODEL FUNCTION?

1. Workers give their labour to the owners. In return, they receive wages which accumulate to become wealth. A certain amount of wealth is deducted for sustaining livelihood, and excess is saved.

2. Owners take labour from workers, take their own labour and capital, and give it to the asset. In return, they receive revenue from the asset. The owners then divide this revenue into three components -
    - Capital (which is stored with the owner, and is invested back into the asset)
    - Wages (which go to the workers)
    - Wealth (which stays with the owners)

3. The asset has a certain level of productivity. Depending on this productivity, and the total amount of labour and capital received, the asset generates revenue. The asset then gives this revenue to the owners.

> This model is a network model. This is because the agents (workers - business owners - assets) are linked to each other.

## WHAT TAKES PLACE AT EVERY TICK?

1. Worker agent gives their labour to the linked owner agent
2. Owner takes the labour given by all workers linked to it
3. Owner inspects their own labour and capital
4. Owner gives the total labour and capital to the asset
5. The asset takes the total labour and capital
6. Based on the productivity, labour and capital - asset generates revenue
7. Asset gives the revenue to owners
8. Owners take this revenue and divide it three ways - capital, wealth and wages
9. Owners add to their capital from the revenue.
10. Owners provide wages to all linked worker agents from the revenue
11. Owners add to their wealth from the revenue
12. Owners deduct a certain amount of wealth for sustaining livelihood.
13. Workers get their wealth from wages
14. Workers deduct a certain amount of wealth for sustaining livelihood.

## WHAT ARE THE CONTENTS OF THIS REPO?

### .gitignore

> Standard .gitignore file that will ignore the unnecessary files: .txt, .xlsx, .png, and pychache folders.  

### Ishwari-private-property.nlogo

> This is the **netlogo code file** that will run the simulation in NetLogo.

### production_main.py

> **This is the main python file that should be run**.  
> 
> The main file takes input from user on which segments of the code should be run. There are two segments:  
1. Generating Data
2. Generating Graphs

> Based on user input, the code will generate data and also generate respective graphs.

### production_simulation.py

> **This file contains the modules to run the simulation code and obtain all the data**.
> 
> Following is a brief summary of the main function:

1. The working directory is set.
2. A java virtual enviornment is initiated.
3. All unique combinations of input parameters are created.
4. For each combination, a new netlogo simulation is triggered in the java environment, without the graphics user interface.
5. Relevant data from each simulation is collected.
6. The simulation is closed.
7. All parameters are completed.
8. The java virtual enviornment is closed.
9. The data is converted into dataframe, cleaned, and stored for analysis.

### production_graph.py

> **This file contains the modules to generate the graphs**.
> 
> Following a brief summary of the main function:

1. 1 dataset is sotred in the main variable.
2. The dataset is cleaned for the X and Y data.
3. X and Y data points are stored to input in the matplotlib graph function.
4. The graph is plotted.
5. The file is converted to png and stored in the working directory.

## HOW DOES ONE SET UP THE CODE?

For each the python code to run, **create a config file** using the provided production_config.md template.  
Then, **run the production_main.py file**!