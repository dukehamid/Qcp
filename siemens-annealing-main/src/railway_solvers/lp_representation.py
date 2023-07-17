from docplex.mp.model import Model

# Initialize the model
mdl = Model(name='train_scheduling')

# Define your parameters
J = ["Train_1", "Train_2"]  # Set of trains
S = {"Train_1": ["Station_1", "Station_2", "Station_3"],
     "Train_2": ["Station_2", "Station_3"]}  # Set of station blocks

d_u = {("Train_1", "Station_1"): 0, ("Train_1", "Station_2"): 0, ("Train_1", "Station_3"): 0,
       ("Train_2", "Station_2"): 0, ("Train_2", "Station_3"): 0}  # Unavoidable delay

d_max = {"Train_1": 5, "Train_2": 5}  # Maximum delay

w = {"Train_1": 1, "Train_2": 0}  # Weights reflecting the trains priority

successor = {("Train_1", "Station_1"): "Station_2", ("Train_1", "Station_2"): "Station_3",
             ("Train_2", "Station_2"): "Station_3"}  # Next station block

tau_1 = {("Train_1", "Station_1", "Station_2"): 2, ("Train_1", "Station_2", "Station_3"): 2,
         ("Train_2", "Station_2", "Station_3"): 2}  # Minimal time for train to give way to another train in the same direction

tau_2 = {("Train_1", "Station_1", "Station_2"): 3, ("Train_1", "Station_2", "Station_3"): 3,
         ("Train_2", "Station_2", "Station_3"): 3}  # Minimal time for train to give way to another train in the opposite direction

sigma_out = {("Train_1", "Station_1"): 0, ("Train_1", "Station_2"): 4, ("Train_1", "Station_3"): 8,
             ("Train_2", "Station_2"): 9, ("Train_2", "Station_3"): 12}  # Timetable time of leaving

time_reserve = {("Train_1", "Station_1", "Station_2"): 1, ("Train_1", "Station_2", "Station_3"): 1,
                ("Train_2", "Station_2", "Station_3"): 1}  # Time reserve

M = 1000  # Large positive number (big-M method)



# Variable Definitions
d = mdl.continuous_var_dict(((j, s) for j in J for s in S), name="d")  # Delay
d_s = mdl.continuous_var_dict(((j, s) for j in J for s in S), name="d_s")  # Secondary delay
y = mdl.binary_var_dict(((j, j_prime, s) for j in J for j_prime in J for s in S), name="y")  # Binary occupation

# Variable Definitions
d = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), name="d")  # Delay
d_s = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), name="d_s")  # Secondary delay
y = mdl.binary_var_dict(((j, j_prime, s) for j in J for j_prime in J for s in S[j]), name="y")  # Binary occupation

# Constraints
for j in J:
    for s in S[j]:
        # Secondary delay should be delay minus unavoidable delay
        mdl.add_constraint(d_s[j, s] == d[j, s] - d_u[j, s])

        # Unavoidable delay should be less than or equal to delay
        mdl.add_constraint(d_u[j, s] <= d[j, s])

        # Delay should be less than or equal to unavoidable delay plus maximum delay
        mdl.add_constraint(d[j, s] <= d_u[j, s] + d_max[j])

        if s != S[j][-1]:  # Exclude the last station block in the route
            next_s = successor[j, s]

            # Minimal passing time
            mdl.add_constraint(d[j, next_s] >= d[j, s] - time_reserve[j, s, next_s])

            for j_prime in J:
                if j != j_prime and s in S[j_prime]:
                    # Single block occupation condition
                    mdl.add_constraint(
                        d[j_prime, s] + M * (1 - y[j, j_prime, s]) >= d[j, s] + sigma_out[j, s] - sigma_out[
                            j_prime, s] + tau_1[j, s, next_s])

                    # Deadlock condition
                    mdl.add_constraint(
                        d[j_prime, s] + M * (1 - y[j, j_prime, s]) >= d[j, s] + sigma_out[j, s] - sigma_out[
                            j_prime, s] + tau_2[j, s, next_s])


# Objective function
objective = mdl.sum((d[j, S[j][-1]] - d_u[j, S[j][-1]]) / d_max[j] * w[j] for j in J)
mdl.minimize(objective)

# Solve the model
solution = mdl.solve()

# Print the solution
if solution:
    print(solution)
    print(f'solution is {j}_{s}')
    for j in J:
        for s in S[j]:
            print(f'd_{j}_{s}={d[j, s].solution_value}')
else:
    print("No solution found")
