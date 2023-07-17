from docplex.mp.model import Model
import numpy as np
# Initialiconvex_delaye the model
mdl = Model(name='train_qubo_scheduling')

J = ["Train_1", "Train_2"]  # Set of trains
S = {"Train_1": ["Station_1", "Station_2", "Station_3"],
     "Train_2": ["Station_2", "Station_3"]}  # Set of station blocks
d_u = {("Train_1", "Station_1"): 0, ("Train_1", "Station_2"): 2, ("Train_1", "Station_3"): 0,
       ("Train_2", "Station_2"): 1, ("Train_2", "Station_3"): 0}  # Unavoidable delay
d_max = {"Train_1": 5, "Train_2": 5}  # Maximum delay
w = {"Train_1": 1, "Train_2": 0}  # Weights reflecting the trains priority
successor = {("Train_1", "Station_1"): "Station_2", ("Train_1", "Station_2"): "Station_3",
             ("Train_2", "Station_2"): "Station_3"}  # Next station block
tau_1 = {("Train_1", "Station_1", "Station_2"): 2, ("Train_1", "Station_2", "Station_3"): 2,
         ("Train_2", "Station_2", "Station_3"): 2}  # Minimal time for train to give way to another train in the same direction
tau_2 = {("Train_1", "Station_1", "Station_2"): 3, ("Train_1", "Station_2", "Station_3"): 3,
         ("Train_2", "Station_2", "Station_3"): 3}  # Minimal time for train to give way to another train in the opposite direction
sigma_out = {("Train_1", "Station_1"): 0, ("Train_1", "Station_2"): 4, ("Train_1", "Station_3"): 8,
             ("Train_2", "Station_2"): 9, ("Train_2", "Station_3"): 12}  # Timetable time of leaving s

M = 1000  # Large positive number (big-M method)

# Define A dictionary before x dictionary
A = {
    (j, s): list(range(d_u[j, s], d_u[j, s] + d_max[j] + 1))
    for j in J
    for s in S[j]
}

# Variable Definitions
d = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), name="d")  # Delay
d_s = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), name="d_s")  # Secondary delay

# Create x dictionary with updated range for d
x = {
    (j, s, k): mdl.binary_var(name=f"x[{j},{s},{k}]")
    for j in J
    for s in S[j]
    for k in range(max(A[j, s]) + 1)
    if k in A[j,s]
}

def common_path(S, j, j_prime):
    # Get the stations for train j
    stations_j = set(S[j])

    # Get the stations for train j_prime
    stations_j_prime = set(S[j_prime])

    # Find the common stations between train j and train j_prime
    common_stations = stations_j.intersection(stations_j_prime)

    # Create a dictionary with train names as keys and common stations as values
    common_path_dict = {
        j: list(common_stations),
        j_prime: list(common_stations)
    }

    return common_path_dict

common_path_dict = common_path(S, J[0], J[1])
print(common_path_dict)

# QUBO of delay representations
for j in J:
    for s in S[j]:
        mdl.add_constraint(d_s[j, s] == d[j, s] - d_u[j, s])
        mdl.add_constraint(d_u[j, s] <= d[j, s])
        mdl.add_constraint(d[j, s] <= d_u[j, s] + d_max[j])

# QUBO of constraints
for j in J:
    # minimal passing time condition
    for s in S[j][:-2]:
        if (j, s) in successor:
            next_s = successor[(j, s)]
            for k in A[j, s]:
                for k_prime in A[j, next_s]:
                    if k_prime < min(k + tau_1[j, s, next_s], d_max[j] + 1):
                        mdl.add_constraint(
                            d[j, s] + tau_1[j, s, next_s] <= d[j, next_s] + M * (1 - (x[j, s, k] * x[j, next_s, k_prime]))
                        )
                        mdl.add_constraint(
                            d[j, s] + tau_1[j, s, next_s] + 1 >= d[j, next_s] - M * (x[j, s, k] * x[j, next_s, k_prime])
                        )
                        mdl.add_constraint(
                            (x[j, s, k] * x[j, next_s, k_prime]) <= x[j, s, k]
                        )
                        mdl.add_constraint(
                            (x[j, s, k] * x[j, next_s, k_prime]) <= x[j, next_s, k_prime]
                        )

# single block occupation condition
for j_prime in J:
    if j != j_prime:
        for s in common_path(S, j, j_prime)[j][:-1]:
            if (j, s) in successor:
                next_s = successor[(j, s)]
                for k in A[j, s]:
                    for k_prime in range(k + sigma_out[j, s] - sigma_out[j_prime, s],
                                        k + sigma_out[j, s] - sigma_out[j_prime, s] + tau_1[j, s, next_s] - 1):
                        if k_prime in A[j_prime, s]:
                            mdl.add_constraint(
                                x[j, s, k] + x[j_prime, s, k_prime] - 1 <= x[j, s, k] * x[j_prime, s, k_prime]
                            )
                            mdl.add_constraint(
                                x[j, s, k] * x[j_prime, s, k_prime] <= x[j, s, k]
                            )
                            mdl.add_constraint(
                                x[j, s, k] * x[j_prime, s, k_prime] <= x[j_prime, s, k_prime]
                            )
                            mdl.add_constraint(
                                x[j, s, k] * x[j_prime, s, k_prime] <= 1
                            )
                            mdl.add_constraint(
                                x[j, s, k] + x[j_prime, s, k_prime] >= 2 - (1 - x[j, s, k] * x[j_prime, s, k_prime]) * M
                            )

    # single block occupation condition
    # for j_prime in J:
    #     if j != j_prime:
    #         #print('DEBUG S',common_path(S[j_prime], j, j_prime))
    #         for s in S[j_prime][:-1]:
    #             if (j, s) in successor:
    #                 next_s = successor[(j, s)]
    #                 for k in A[j, s]:
    #                     for k_prime in range(k + sigma_out[j, s] - sigma_out[j_prime, s],
    #                                         k + sigma_out[j, s] - sigma_out[j_prime, s] + tau_1[j, s, next_s] - 1):
    #                         if k_prime in A[j_prime, s]:
    #                             mdl.add_constraint(
    #                                 x[j, s, k] + x[j_prime, s, k_prime] - 1 <= x[j, s, k] * x[j_prime, s, k_prime]
    #                             )
    #                             mdl.add_constraint(
    #                                 x[j, s, k] * x[j_prime, s, k_prime] <= x[j, s, k]
    #                             )
    #                             mdl.add_constraint(
    #                                 x[j, s, k] * x[j_prime, s, k_prime] <= x[j_prime, s, k_prime]
    #                             )
    #                             mdl.add_constraint(
    #                                 x[j, s, k] * x[j_prime, s, k_prime] <= 1
    #                             )
    #                             mdl.add_constraint(
    #                                 x[j, s, k] + x[j_prime, s, k_prime] >= 2 - (1 - x[j, s, k] * x[j_prime, s, k_prime]) * M
    #                             )

                        # Deadlock condition
                        for k_prime in range(k + sigma_out[j, s] - sigma_out[j_prime, next_s],
                                                k + sigma_out[j, s] - sigma_out[j_prime, next_s] + tau_2[j, s, next_s] - 1):
                            if k_prime in A[j_prime, next_s]:
                                mdl.add_constraint(
                                    x[j, s, k] + x[j_prime, next_s, k_prime] - 1 <= x[j, s, k] * x[j_prime, next_s, k_prime]
                                )
                                mdl.add_constraint(
                                    x[j, s, k] * x[j_prime, next_s, k_prime] <= x[j, s, k]
                                )
                                mdl.add_constraint(
                                    x[j, s, k] * x[j_prime, next_s, k_prime] <= x[j_prime, next_s, k_prime]
                                )
                                mdl.add_constraint(
                                    x[j, s, k] * x[j_prime, next_s, k_prime] <= 1
                                )
                                mdl.add_constraint(
                                    x[j, s, k] + x[j_prime, next_s, k_prime] >= 2 - (1 - x[j, s, k] * x[j_prime, next_s, k_prime]) * M
                                ) 

def calculate_f(train, station):
    hat_d = (d[train, station] - d_u[train, station]) / d_max[train]
    #constraint = mdl.add_constraint(hat_d >= 0)
    #comparison_expr = mdl.sum([hat_d, -0])
    # if hat_d == 0:#hat_d == 0:
    #     return 0
    # elif hat_d == 1:#hat_d == 1:
    #     return max(hat_d, 0)
    # else:
    return hat_d

def calculate_objective():
    objective_value = 0
    for train in J:
        for station in S[train]:
            for delay in A[(train, station)]:
                f_value = calculate_f(train, station)
                objective_value += f_value * x[(train, station, delay)]
    return objective_value

objective = mdl.sum((d[j,s] - d_u[j, s]) / d_max[j] for j in J for s in S[j])#calculate_objective()

""" # Calculate d_weights
d_weights = {(j, s, k): (d[j,s] - d_u[j, s]) / d_max[j] for (j, s, k) in x}

#Define new variables r represents the computation with d_weights
r = mdl.continuous_var_dict(((j, s, k) for j in J for s in S[j] for k in range(d_max[j])), name="r")

# Add linearization constraints
for (j, s, k) in x:
    mdl.add_constraint(r.get((j, s, k), 0) >= 0)
    #mdl.add_constraint(r.get((j, s, k), 0) >= d_weights[j, s, k] * x[j, s, k])
    mdl.add_constraint(r.get((j, s, k), 0) <= d_max[j] * x[j, s, k])

# Modify the objective function
objective = mdl.sum(r.get((j, s, k), 0) for (j, s, k) in x) """

# qubo_objective=mdl.sum((d[j,s] - d_u[j, s]) / d_max[j] for j in J for s in S[j])

#Penalty terms

# Add quadratic penalty terms for the hard constraints
#p_sum, p_pair > max{w1,w2}
p_sum = 1.75  # positive constant
p_pair = 1.75  # positive constant

#k are equal: two trains are not allowed to depart from the stations at the same time
penalty_pair = p_pair * mdl.sum(
    x.get((j, s, k), 0) * x.get((j_prime, s_prime, k), 0) + x.get((j_prime, s_prime, k_prime), 0) * x.get((j, s, k_prime), 0)
    for j in J
    for j_prime in J if j != j_prime
    for s in S[j]
    for s_prime in S[j_prime]
    for k in A[j, s]
    for k_prime in A[j_prime, s_prime]
)

# k not equal: each train departs from each station once and only once
penalty_sum = p_sum * mdl.sum(
    mdl.sum(
        mdl.sum(
            x.get((j, s, k), 0) * x.get((j, s, k_prime), 0)
            for j_prime in J if j_prime != j
            for s_prime in S[j_prime]
            for k_prime in A[j_prime, s_prime]
        ) - x[j, s, k] ** 2
        for k in A[j, s]
    )
    for j in J
    for s in S[j]
)

penalty_objective = objective + penalty_sum + penalty_pair

mdl.minimize(penalty_objective)

# Set optimality target to 2
mdl.parameters.optimalitytarget = 0

# Solve the model
solution = mdl.solve()

mdl.print_information()

if solution:
    print(solution)
    # print(f'solution is {j}_{s}')
    # for j in J:
    #     for s in S[j]:
    #         for k in A[j,s]:
    #             #print(f'd_{j}_{s}={d[j, s].solution_value}')
    #             print(f'x_{j}_{s}_{k} = {x[j, s, k].solution_value}')

else:
    print("No solution found")