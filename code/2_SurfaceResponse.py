import numpy as np
from collections import deque 
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression


class Inventory():

    def __init__(self):
        self.average_arrival = 10
        self.outcomes = [1, 2, 3, 4]
        self.probabilities = [1/6, 1/3, 1/3, 1/6]
        self.demand_distr = lambda size: np.random.choice(
            self.outcomes, size=size,
            p=self.probabilities
        )
        self.starting_inventory = 100
        self.max_lead_time = 3
        self.fixed_cost = 32
        self.variable_cost = 3
        self.holding_cost = 1
        self.backlog_cost = 5

    def run_simulation(self, n, s, d, verbose=False, seed=None):
        np.random.seed(seed)
        lead_times = np.random.randint(low=1, high=self.max_lead_time, size=n)
        customers = np.random.poisson(lam=self.average_arrival, size=n)
        # generate demands
        demands = np.zeros(n)
        for i in range(n):
            demands[i] = sum(self.demand_distr(customers[i]))
        # print(np.average(demands))
        total_costs = np.zeros(n)
        inventory = np.zeros(n)
        inventory[0] = self.starting_inventory
        arrivals = deque([0] * self.max_lead_time, maxlen=self.max_lead_time)
        
        for i in range(1, n):
            # update arrivals
            arrival = arrivals.popleft()
            if verbose: print(f"arrival: {arrival}")
            arrivals.append(0) # restore lenght
            # update inventory
            inventory[i] = inventory[i-1] - demands[i-1] + arrival
            if verbose: print(f"{i}] inventory: {inventory[i]} = {inventory[i-1]} - {demands[i-1]} + {arrival}")
            # update with orders
            if inventory[i] <= s:
                arrivals[lead_times[i]] += d
                order_cost = self.fixed_cost + self.variable_cost * d
            else:
                order_cost = 0
            if verbose: print(f"new arrivals: {arrivals} (order {d} but lead time {lead_times[i]})")
            # compute cost:
            tot_inv_cost = self.holding_cost * max(inventory[i], 0)
            tot_back_cost = self.backlog_cost * max(-inventory[i], 0)
            total_cost = order_cost + tot_inv_cost + tot_back_cost
            if verbose: print(f"total_cost: {total_cost} ( {order_cost} + {tot_inv_cost} + {tot_back_cost} )")
            if verbose: print("---")
            total_costs[i] = total_cost
        return total_costs



inv = Inventory()

# s values:
s_low = 0
s_high = 30

# d values:
d_low = 10
d_high = 100

T_max = 12
# get results
n_reps = 10
dict_res = {(s,d): {} for s in range(s_low, s_high+1) for d in range(d_low, d_high+1)}

for s in range(s_low, s_high+1):
    for d in range(d_low, d_high+1):
        tmp = np.zeros(n_reps)
        for i in range(n_reps):
            tmp[i] = np.average(inv.run_simulation(T_max, s, d, seed=i))
        # notice that the element of tmp are iid
        dict_res[s, d] = np.average(tmp)



effect_s = ((dict_res[s_high, d_high] - dict_res[s_low, d_high]) + (dict_res[s_high, d_low] - dict_res[s_low, d_low])) / 2 
effect_d = ((dict_res[s_high, d_high] - dict_res[s_high, d_low]) + (dict_res[s_low, d_high] - dict_res[s_low, d_low])) / 2 
effect_sd = ((dict_res[s_high, d_high] - dict_res[s_low, d_high]) - (dict_res[s_high, d_low] - dict_res[s_low, d_low])) / 2 

print(f"effect_s: {effect_s:.2f}")
print(f"effect_d: {effect_d:.2f}")
print(f"effect_sd: {effect_sd:.2f}")


# create dataset for metamodel
X = np.zeros((len(dict_res),5))
y = np.zeros(len(dict_res))

count = 0
for key, ele in dict_res.items():
    X[count, 0] = key[0]
    X[count, 1] = key[1]
    X[count, 2] = key[0] * key[1]
    X[count, 3] = key[0] ** 2
    X[count, 4] = key[1] ** 2
    y[count] = ele
    count += 1

# Step 2: Initialize the MinMaxScaler with the desired range (-1, 1)
scaler = MinMaxScaler(feature_range=(-1, 1))

# Step 3: Fit the scaler to the data and transform it
X_normalized = scaler.fit_transform(X)
print(X_normalized)



# fit metamodel

# Create and fit the Linear Regression model
model = LinearRegression()
model.fit(X_normalized, y)

# Get the model parameters
slope = model.coef_        # Coefficient (slope)
intercept = model.intercept_   # Intercept

# Print the parameters
print(f"Slope (Coefficient): {slope}")
print(f"Intercept: {intercept}")
response_function = lambda s, d: intercept + slope[0]*s + slope[1]*d + slope[2]*s*d + slope[3]*s**2 + slope[4]*d**2

x1_grad_0 = (2 * slope[0] * slope[4] - slope[1] * slope[2]) / (slope[2] ** 2 - 4 * slope[3] * slope[4])
x2_grad_0 = (2 * slope[1] * slope[3] - slope[0] * slope[2]) / (slope[2] ** 2 - 4 * slope[3] * slope[4])

autoval_1 = slope[3] + slope[4] + np.sqrt(slope[3] ** 2 + slope[4] ** 2 - 2 * slope[3] * slope[4] + slope[2] ** 2)
autoval_2 = slope[3] + slope[4] - np.sqrt(slope[3] ** 2 + slope[4] ** 2 - 2 * slope[3] * slope[4] + slope[2] ** 2)

print(f'Il punto ({x1_grad_0},{x2_grad_0}) è un punto di ', end = '')
if autoval_1 > 0 and autoval_2 > 0:
    print('minimo')
elif autoval_1 < 0 and autoval_2 < 0:
    print('massimo')
else:
    print('sella')

# Optimize metamodel

# Create mesh grid for x1 and x2 for surface visualization
x1_vals = np.linspace(x1_grad_0 - 2, x1_grad_0 + 2, 100)
x2_vals = np.linspace(x2_grad_0 - 2, x2_grad_0 + 2, 100)
x1_grid, x2_grid = np.meshgrid(x1_vals, x2_vals)

# Compute the response values for the mesh grid
z_vals = response_function(x1_grid, x2_grid)

# Create a 3D plot for the response surface
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x1_grid, x2_grid, z_vals, cmap='viridis', edgecolor='none')
ax.set_title("Response Surface")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
ax.set_zlabel("Response f(x1, x2)")
plt.show()

# Create a contour plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(x1_grid, x2_grid, z_vals, cmap='viridis', levels=50)
plt.colorbar(contour)
plt.title("Contour Plot of the Response Surface")
plt.xlabel("x1")
plt.ylabel("x2")
plt.show()

# Optimization: Find the optimal values for x1 and x2
def objective_function(x):
    return response_function(x[0], x[1])

# Initial guess for optimization
initial_guess = [x1_grad_0, x2_grad_0]

# Perform optimization
bnds = ((x1_grad_0 - 2, x1_grad_0 + 2), (x1_grad_0 - 2, x1_grad_0 + 2))
result = minimize(objective_function, initial_guess, bounds=bnds)

# Display the optimal solution
optimal_x1, optimal_x2 = result.x
optimal_response = response_function(optimal_x1, optimal_x2)

print(f"Optimal s: {optimal_x1}")
print(f"Optimal d: {optimal_x2}")
print(f"Optimal response: {optimal_response}")



# create new dataset
possible_s = [0, 10, 20, 30, 100]
possible_d = [10, 50, 100, 200]
n_data = len(possible_s) * len(possible_d)
X = np.zeros((n_data,5))
y = np.zeros(n_data)

count = 0
for s in possible_s:
    for d in possible_d:
        tmp = np.zeros(n_reps)
        for i in range(n_reps):
            tmp[i] = np.average(inv.run_simulation(T_max, s, d, seed=i))
        X[count, 0] = s
        X[count, 1] = d
        X[count, 2] = s*d
        X[count, 3] = s**2
        X[count, 4] = d**2
        y[count] = np.average(tmp)
        count += 1

# Step 2: Initialize the MinMaxScaler with the desired range (-1, 1)
scaler = MinMaxScaler(feature_range=(-1, 1))

# Step 3: Fit the scaler to the data and transform it
X_normalized = scaler.fit_transform(X)
print(X_normalized)