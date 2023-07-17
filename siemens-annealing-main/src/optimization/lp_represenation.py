from docplex.mp.model import Model

def optimize_schedule_lp(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out, M):
    # Initialize the model
    mdl = Model(name='train_scheduling')

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
                mdl.add_constraint(d[j, next_s] >= d[j, s])

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
    with open("lp_solution.json", "w") as solfile:
        solfile.write(mdl.solution.to_string())

    if solution:
        # Convert solution to dictionary
        solution_dict = {}
        # Convert solution to dictionary
        solution_dict = {}
        for j in J:
            for s in S[j]:
                solution_dict[f'd_{j}_{s}'] = d[j, s].solution_value
                #solution_dict[f'x_{j}_{s}_{d}'] = x[j, s, d].solution_value

        # Return the solution dictionary
        return solution_dict
    else:
        print("No solution found")
        return None

    # if solution:
    #     print(solution)
    #     for j in J:
    #         for s in S[j]:
    #             print(f'd_{j}_{s}={d[j, s].solution_value}')
    # else:
    #     print("No solution found")