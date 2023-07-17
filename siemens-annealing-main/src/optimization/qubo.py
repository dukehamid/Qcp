from docplex.mp.model import Model

def optimize_schedule_qubo(Trains, Stations, unavoid_delay, max_delay, w, successor, tau_1, tau_2, sigma_out, M):
    # Initialiconvex_delaye the model
    mdl = Model(name='train_qubo_scheduling')

    # Define all_delays dictionary before x dictionary
    all_delays = {
        (train, station): list(range(unavoid_delay[train, station], unavoid_delay[train, station] + max_delay[train] + 1))
        for train in Trains
        for station in Stations[train]
    }
    #print(all_delays)
    # Variable Definitions
    Delays = mdl.continuous_var_dict(((train, station) for train in Trains for station in Stations[train]), name="Delays")  # Delay
    secondary_delay = mdl.continuous_var_dict(((train, station) for train in Trains for station in Stations[train]), name="secondary_delay")  # Secondary delay

    # Create x dictionary with updated range for Delays
    x = {
        (train, station, delay): mdl.binary_var(name="x_" + str(train) + "_" + str(station) + "_" + str(delay))
        for train in Trains
        for station in Stations[train]
        for delay in range(max(all_delays[(train,station)]) + 1)
        if delay in all_delays[train, station]
    }
    variables = {}
    index = 0
    for train in Trains:
        for station in Stations[train]:
            variables[(train, station)] = index
            index += 1

    # Initialize the QUBO matrix
    num_variables = len(variables)
    Q = [[0 for _ in range(num_variables)] for _ in range(num_variables)]

    def common_path(Stations, j, j_prime):
        # Get the stations for train j
        stations_j = set(Stations[j])

        # Get the stations for train j_prime
        stations_j_prime = set(Stations[j_prime])

        # Find the common stations between train j and train j_prime
        common_stations = stations_j.intersection(stations_j_prime)

        # Create a dictionary with train names as keys and common stations as values
        common_path_dict = {
            j: list(common_stations),
            j_prime: list(common_stations)
        }

        return common_path_dict

    # QUBO of delay representations
    for train in Trains:
        for station in Stations[train]:
            mdl.add_constraint(secondary_delay[train, station] == Delays[train, station] - unavoid_delay[train, station])
            mdl.add_constraint(unavoid_delay[train, station] <= Delays[train, station])
            mdl.add_constraint(Delays[train, station] <= unavoid_delay[train, station] + max_delay[train])

#   # QUBO of constraints
    for train in Trains:
#         # minimal passing time condition
        for station in Stations[train][:-2]:
            if (train, station) in successor:
                next_station = successor[(train, station)]
                for delay in all_delays[train, station]:
                    for delay_prime in all_delays[train, next_station]:
                        if delay_prime < min(delay + tau_1[train, station, next_station], max_delay[train] + 1):        
                            mdl.add_constraint(
                                Delays[train, station] + tau_1[train, station, next_station] <= Delays[train, next_station] + M * (1 - (x[train, station, delay] * x[train, next_station, delay_prime]))
                            )
                            mdl.add_constraint(
                                Delays[train, station] + tau_1[train, station, next_station] + 1 >= Delays[train, next_station] - M * (x[train, station, delay] * x[train, next_station, delay_prime])
                            )
                            mdl.add_constraint(
                                (x[train, station, delay] * x[train, next_station, delay_prime]) <= x[train, station, delay]
                            )
                            mdl.add_constraint(
                                (x[train, station, delay] * x[train, next_station, delay_prime]) <= x[train, next_station, delay_prime]
                            )  

        # single block occupation condition
        for train_prime in Trains:
            if train != train_prime:
                for station in common_path(Stations, train, train_prime)[train][:-1]:
                    if (train, station) in successor:
                        next_s = successor[(train, station)]
                        for delay in all_delays[train, station]:
                            for k_prime in range(delay + sigma_out[train, station] - sigma_out[train_prime, station],
                                                delay + sigma_out[train, station] - sigma_out[train_prime, station] + tau_1[train, station, next_s] - 1):
                                if k_prime in all_delays[train_prime, station]:
                                    mdl.add_constraint(
                                        x[train, station, delay] + x[train_prime, station, k_prime] - 1 <= x[train, station, delay] * x[train_prime, station, k_prime]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, k_prime] <= x[train, station, delay]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, k_prime] <= x[train_prime, station, k_prime]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, k_prime] <= 1
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] + x[train_prime, station, k_prime] >= 2 - (1 - x[train, station, delay] * x[train_prime, station, k_prime]) * M
                                    )
                            
                                # Deadlock condition
                                for delay_prime in range(delay + sigma_out[train, station] - sigma_out[train_prime, next_station],
                                                        delay + sigma_out[train, station] - sigma_out[train_prime, next_station] +
                                                        tau_2.get((train, station, next_station), 0)):
                                                        #tau_2[train, station, next_station] - 1):   tau_2.get(('21', '105', '103'), 0))
                                    if delay_prime in all_delays[train_prime, next_station]:
                                        mdl.add_constraint(
                                            x[train, station, delay] + x[train_prime, next_station, delay_prime] - 1 <= x[train, station, delay] * x[train_prime, next_station, delay_prime]
                                        )
                                        mdl.add_constraint(
                                            x[train, station, delay] * x[train_prime, next_station, delay_prime] <= x[train, station, delay]
                                        )
                                        mdl.add_constraint(
                                            x[train, station, delay] * x[train_prime, next_station, delay_prime] <= x[train_prime, next_station, delay_prime]
                                        )
                                        mdl.add_constraint(
                                            x[train, station, delay] * x[train_prime, next_station, delay_prime] <= 1
                                        )
                                        mdl.add_constraint(
                                            x[train, station, delay] + x[train_prime, next_station, delay_prime] >= 2 - (1 - x[train, station, delay] * x[train_prime, next_station, delay_prime]) * M
                                        ) 
    d_hat_values = []
    def f_weight(delay, train, station):
        d_hat = (delay - unavoid_delay[train, station]) / max_delay[train]
        if d_hat == 0:
            d_hat_values.append
            return 0
        elif d_hat == 1:
            max_d_hat = max(d_hat_values,default=0)
            return max_d_hat
        else:
            return d_hat
    ##objective
    objective = mdl.sum((Delays[train, station] - unavoid_delay[train, station]) / max_delay[train] 
                        for train in Trains for station in Stations[train])
    #objective = calculate_objective()

    # Penalty terms

    # Add quadratic penalty terms for the hard constraints
    # p_sum, p_pair > max{w1,w2}
    p_sum = 1.75  # positive constant
    p_pair = 1.75  # positive constant

    # delay are equal: two trains are not allowed to depart from the stations at the same time
    penalty_pair = p_pair * mdl.sum(
        x.get((train, station, delay), 0) * x.get((train_prime, s_prime, delay), 0) + x.get((train_prime, s_prime, delay_prime), 0) * x.get(
            (train, station, delay_prime), 0)
        for train in Trains
        for train_prime in Trains if train != train_prime
        for station in Stations[train]
        for s_prime in Stations[train_prime]
        for delay in all_delays[train, station]
        for delay_prime in all_delays[train_prime, s_prime]
    )

    penalty_objective = objective + penalty_pair #+ penalty_sum 

    mdl.minimize(penalty_objective)
    # Set optimality target to 2
    mdl.parameters.optimalitytarget = 0

    # Solve the model
    solution = mdl.solve()

    mdl.print_information()
    with open("solution.txt", "w") as solfile:
        solfile.write(mdl.solution.to_string())

    if solution:
        # Convert solution to dictionary
        solution_dict = {}
        for train in Trains:
            for station in Stations[train]:
                for delay in all_delays[train,station]:
                    solution_dict[f'x_{train}_{station}'] = Delays[train, station].solution_value
                    #print(f'x_{train}_{station}_{delay} = {x[train, station, delay].solution_value}')
                #print(f'd_{train}_{station} = {d[train, station].solution_value}')
        # Return the solution dictionary
        return solution_dict
    else:
        print("No solution found")
        return None
    





"""         # single block occupation condition
        for train_prime in Trains:
            if train != train_prime:
                for station in Stations[train_prime][:-1]:
                    if (train, station) in successor:
                        next_station = successor[(train, station)]
                        for delay in all_delays[train, station]:
                            for delay_prime in range(delay + sigma_out[train, station] - sigma_out[train_prime, station],
                                                delay + sigma_out[train, station] - sigma_out[train_prime, station] + tau_1[train, station, next_station] - 1):
                                if delay_prime in all_delays[train_prime, station]:
                                    mdl.add_constraint(
                                        x[train, station, delay] + x[train_prime, station, delay_prime] - 1 <= x[train, station, delay] * x[train_prime, station, delay_prime]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, delay_prime] <= x[train, station, delay]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, delay_prime] <= x[train_prime, station, delay_prime]
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] * x[train_prime, station, delay_prime] <= 1
                                    )
                                    mdl.add_constraint(
                                        x[train, station, delay] + x[train_prime, station, delay_prime] >= 2 - (1 - x[train, station, delay] * x[train_prime, station, delay_prime]) * M
                                    ) """