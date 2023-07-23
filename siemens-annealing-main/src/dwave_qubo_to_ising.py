from dwave.system import DWaveSampler, EmbeddingComposite
from src.railway_solvers.qubo import mdl


def cplex_qubo_to_ising(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out, M):
    # Define A dictionary before x dictionary
    A = {(j, s): list(range(d_u[j, s], d_u[j, s] + d_max[j] + 1)) for j in J for s in S[j]}

    # Variable Definitions
    d = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), lb=0, name="d")  # Delay
    d_s = mdl.continuous_var_dict(((j, s) for j in J for s in S[j]), lb=0, name="d_s")  # Secondary delay

    # Create x dictionary with updated range for d
    x = {(j, s, k): mdl.binary_var(name=f"x[{j},{s},{k}]") for j in J for s in S[j] for k in
         range(d_u[j, s], d_u[j, s] + d_max[j] + 1)}

    variables = {}
    index = 0
    for train in J:
        for station in S[train]:
            variables[(train, station)] = index
            index += 1

    # Connect x and d
    for j in J:
        for s in S[j]:
            mdl.add_constraint(d[j, s] == mdl.sum(k * x[j, s, k] for k in A[j, s]))

    # QUBO of delay representations
    for j in J:
        for s in S[j]:
            mdl.add_constraint(d_s[j, s] == d[j, s] - d_u[j, s])
            mdl.add_constraint(d_u[j, s] <= d[j, s])
            mdl.add_constraint(d[j, s] <= d_u[j, s] + d_max[j])
            if (j, s) in successor:
                next_s = successor[(j, s)]
                mdl.add_constraint(d[j, s] <= d[j, next_s])

    # QUBO of constraints
    for j in J:
        for s in S[j][:-1]:
            if (j, s) in successor:
                next_s = successor[(j, s)]
                for k in A[j, s]:
                    for k_prime in A[j, next_s]:
                        if k_prime < min(k + tau_1[j, s, next_s], d_max[j] + 1):
                            mdl.add_constraint(d[j, s] + tau_1[j, s, next_s] <= d[j, next_s] + M * (
                                    1 - x[j, s, k] * x[j, next_s, k_prime]))
                            mdl.add_constraint(
                                d[j, s] + tau_1[j, s, next_s] + 1 >= d[j, next_s] - M * x[j, s, k] * x[
                                    j, next_s, k_prime])
                            mdl.add_constraint(x[j, s, k] * x[j, next_s, k_prime] <= x[j, s, k])
                            mdl.add_constraint(x[j, s, k] * x[j, next_s, k_prime] <= x[j, next_s, k_prime])

    def add_constraints(mdl, x, j, s, k, j_prime, s_prime, k_prime, M):
        mdl.add_constraint(x[j, s, k] + x[j_prime, s_prime, k_prime] - 1 <= x[j, s, k] * x[j_prime, s_prime, k_prime])
        mdl.add_constraint(x[j, s, k] * x[j_prime, s_prime, k_prime] <= x[j, s, k])
        mdl.add_constraint(x[j, s, k] * x[j_prime, s_prime, k_prime] <= x[j_prime, s_prime, k_prime])
        mdl.add_constraint(
            x[j, s, k] + x[j_prime, s_prime, k_prime] >= 2 - (1 - x[j, s, k] * x[j_prime, s_prime, k_prime]) * M)

    for j in J:
        for j_prime in J:
            if j != j_prime:
                for s in S[j_prime][:-1]:
                    if (j, s) in successor:
                        next_s = successor[(j, s)]
                        for k in A[j, s]:
                            start = k + sigma_out[j, s] - sigma_out[j_prime, s]
                            end_1 = start + tau_1[j, s, next_s] - 1
                            for k_prime in [kp for kp in range(start, end_1) if kp in A[j_prime, s]]:
                                add_constraints(mdl, x, j, s, k, j_prime, s, k_prime, M)
                            start = k + sigma_out[j, s] - sigma_out[j_prime, next_s]
                            end_2 = start + tau_2[j, s, next_s] - 1
                            for k_prime in [kp for kp in range(start, end_2) if kp in A[j_prime, next_s]]:
                                add_constraints(mdl, x, j, s, k, j_prime, next_s, k_prime, M)

    # def calculate_objective():
    #     objective_value = 0
    #     for train in Trains:
    #         for station in Stations[train]:
    #             for delay in all_delays[(train, station)]:
    #                 hat_d = (Delays[train, station] - unavoid_delay[train, station]) / max_delay[train]
    #                 f_value = hat_d
    #                 #f_value = calculate_f(delay, Trains, Stations, unavoid_delay, max_delay)
    #                 objective_value += f_value * x[(train, station, delay)]
    #     return objective_value

    # objective = mdl.sum((Delays[train, station] - unavoid_delay[train, station]) / max_delay[train]
    #                     for train in Trains for station in Stations[train])
    # objective = calculate_objective()

    # Objective function
    # Calculate d_weights
    d_weights = {(j, s, k): (d[j, s] - d_u[j, s]) / d_max[j] for (j, s, k) in x}

    # Define new variables r represents the computation with d_weights
    r = mdl.continuous_var_dict([(j, s) for j in J for s in S[j]], lb=0, ub=1, name='r')

    for (j, s) in d:
        mdl.add_constraint(r[j, s] == (d[j, s] - d_u[j, s]) / d_max[j])

    # Modify the objective function
    objective = mdl.sum(r[j, s] * w[j] for j in J for s in S[j])

    # Penalty terms

    # Add quadratic penalty terms for the hard constraints
    p_pair = 1.75  # positive constant

    # delay are equal: two trains are not allowed to depart from the stations at the same time
    penalty_pair = p_pair * mdl.sum(
        x[j, s, k] * x[j_prime, s_prime, k]
        for j in J
        for j_prime in filter(lambda jp: jp != j, J)
        for s in S[j]
        for s_prime in S[j_prime]
        for k in A[j, s]
        if (j, s, k) in x and (j_prime, s_prime, k) in x
    )

    penalty_objective = objective + penalty_pair

    mdl.minimize(penalty_objective)
    mdl.parameters.optimalitytarget = 0

    # QUBO coefficients and offset
    qubo = mdl.to_qubo(penalty_objective)

    # Convert QUBO coefficients to Ising coefficients
    linear = {}
    quadratic = {}

    for (i, j), value in qubo.items():
        if i == j:
            linear[i] = value
        else:
            quadratic[(i, j)] = value

    # Optional: Add offset to the Ising coefficients to ensure the ground state energy
    # corresponds to the optimal solution of the QUBO.
    offset = mdl.objective.constant

    # Return the Ising coefficients and offset
    return linear, quadratic, offset


def solve_ising_on_dwave(linear, quadratic, offset):
    sampler = EmbeddingComposite(DWaveSampler())

    # Submit the Ising problem to D-Wave Leap for solving
    response = sampler.sample_ising(linear, quadratic, offset=offset)

    # Process and analyze the results
    if response:
        for sample, energy in response.data(['sample', 'energy']):
            print(f'Solution: {sample}, Energy: {energy}')

        return response
    else:
        print("No solution found")
        return None


if __name__ == "__main__":
    # Call the function to convert the CPLEX QUBO to Ising model
    linear, quadratic, offset = cplex_qubo_to_ising(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out, M)

    # Call the function to solve the Ising model on D-Wave Leap
    solve_ising_on_dwave(linear, quadratic, offset)
