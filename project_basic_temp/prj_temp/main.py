import json
from data import *
from instances import *
from solvers import *

hospital_data = upload_data('./data/test05.json') # Uploading hospital data
hospital =Hospital(hospital_data) # Creating Hospital class

with open("./settings/solver_setting.json") as f:
    solver_setting = json.load(f) # Uploading solver settings

ga = Ga_Solver(solver_setting,hospital) # Creating Ga_solver class
solution= ga.solve() # Solving the optimization problem with the Ga_solver
print(f'Fitness of the solution found: {solution["Optimal fitness"]}')

with open("./data/ihtc2024_test_solutions/sol_test05.json") as f:
    real_solution = json.load(f)
real_optimal_cost=real_solution["costs"]
print(f'Best costs: {real_optimal_cost}')
