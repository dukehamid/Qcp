import os

from conflict_detection.Conflicts import detect_conflicts, print_conflicts
from conflict_detection.Delays import detect_delays
from helpers.Helper_Functions import load_json_file, extract_problem_instance_from_json, create_sigma_out, \
    extract_routes, extract_max_delays, extract_successor, extract_tau_values
from helpers.add_delays import generate_delayed_schedules
from helpers.bundle_optimization_outputs import save_optimization_output
from helpers.calculate_optimized_timetable import optimize_timetable
from helpers.generate_json import generate_initial_timetable
from helpers.plot_railnetwork import plot_all_railnetworks
from helpers.plot_schedules import plot_all_schedules
from optimization.lp_represenation import optimize_schedule_lp
from optimization.qubo import optimize_schedule_qubo

# Setup
qubits, initial_json, d_max = generate_initial_timetable(num_stations=6, num_trains=4, d_max=5)
plot_all_railnetworks()
plot_all_schedules()

# Check if the generated JSON already contains conflicts
initial_data = load_json_file(initial_json)
initial_instance = extract_problem_instance_from_json(initial_data)
conflicts = detect_conflicts(initial_instance)

if conflicts:
    # Rename json_path to include "_initial_conflicted_timetable.json"
    dir_name, file_name = os.path.split(initial_json)
    conflicted_file_name = file_name.replace("_initial_timetable.json", "_initial_conflicted_timetable.json")
    conflicted_json = os.path.join(dir_name, conflicted_file_name)
    os.rename(initial_json, conflicted_json)

    initial_conflicted_data = initial_data
    initial_conflicted_instance = extract_problem_instance_from_json(conflicted_json)

    # Detect Delays (pseudo calculation, since no actual comparison is made)
    print("\nDelays:")
    delayed, delay_amounts = detect_delays(initial_conflicted_instance, initial_conflicted_instance)

    # Further execution with already conflicted initial file
    print("\nConflict detected! Starting with optimization...")
    J = [str(train.train_id) for train in initial_conflicted_instance.trains]  # Set of trains
    S = extract_routes(conflicted_json)  # Set of stations for each train
    d_u = {(str(j), str(s)): delay_amounts[(j, s)] for j, s in delay_amounts}  # Unavoidable delay
    d_max = extract_max_delays(initial_conflicted_instance)  # Maximum delay
    w = {str(train.train_id): train.priority for train in initial_conflicted_instance.trains}  # Weights reflecting the trains priority
    successor = extract_successor(initial_conflicted_instance)  # Next station block
    tau_1, tau_2 = extract_tau_values(initial_conflicted_instance)  # Minimal time for train to give way to another train in the same/opposite direction
    sigma_out = create_sigma_out(initial_conflicted_instance)  # Timetable time of leaving
    sigma_out_par = {(str(j), str(s)): sigma_out[(j, s)] for j, s in sigma_out}
    M = 1000  # Large positive number (big-M method)

    # Optimization with lp -> reference values for QUBO
    print("Optimizing with LP:")
    optimization_lp_output = optimize_schedule_lp(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par,M)
    print("-" * 30)

    # Optimization with QUBO
    print("Optimizing with QUBO:")
    optimization_qubo_output = optimize_schedule_qubo(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par, M)
    print("-" * 30)

    # Bundle optimization values in JSON file
    output_path = save_optimization_output(initial_json, delayed, delay_amounts, conflicts, optimization_lp_output, optimization_qubo_output)

    # Calculate optimized JSON with schedules
    optimized_json = optimize_timetable(conflicted_json, output_path)

    # Verification: No more conflicts -> again in a valid schedule
    print(optimized_json)
    optimized_data = load_json_file(optimized_json)
    optimized_instance = extract_problem_instance_from_json(optimized_data)

    still_conflicted = detect_conflicts(optimized_instance)

    if still_conflicted:
        print("Optimization was not successful! Conflict count != 0")
        print_conflicts(still_conflicted)
    else:
        print("Optimization was  successful! Conflict count == 0")

else:
    delayed_json = generate_delayed_schedules(initial_json, d_max)
    delayed_data = load_json_file(delayed_json)

    # Further execution with initial file and conflicted delayed file
    initial_instance = extract_problem_instance_from_json(initial_data)
    problem_instance = extract_problem_instance_from_json(delayed_data)

    # Detect Delays
    print("\nDelays:")
    delayed, delay_amounts = detect_delays(initial_instance, problem_instance)

    # if Delay detected, check for conflicts
    if delayed:
        print("\nDelay detected! Checking for conflicts...")
        conflicts = detect_conflicts(problem_instance)

        if conflicts:
            print("\nConflict detected! Starting with optimization...")

            J = [str(train.train_id) for train in problem_instance.trains]  # Set of trains
            S = extract_routes(delayed_data)  # Set of stations for each train
            d_u = {(str(j), str(s)): delay_amounts[(j, s)] for j, s in delay_amounts}  # Unavoidable delay
            d_max = extract_max_delays(delayed_data)  # Maximum delay
            w = {str(train.train_id): train.priority for train in problem_instance.trains}  # Weights reflecting the trains priority
            successor = extract_successor(delayed_data)  # Next station block
            tau_1, tau_2 = extract_tau_values(delayed_data)  # Minimal time for train to give way to another train in the same/opposite direction
            sigma_out = create_sigma_out(problem_instance)  # Timetable time of leaving
            sigma_out_par = {(str(j), str(s)): sigma_out[(j, s)] for j, s in sigma_out}
            M = 1000  # Large positive number (big-M method)

            # Optimization with lp -> reference values for QUBO
            print("Optimizing with LP:")
            optimization_lp_output = optimize_schedule_lp(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par,M)
            print("-" * 30)

            # Optimization with QUBO
            print("Optimizing with QUBO:")
            optimization_qubo_output = optimize_schedule_qubo(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par, M)
            print("-" * 30)

            # Bundle optimization values in JSON file
            output_path = save_optimization_output(initial_json, delayed, delay_amounts, conflicts, optimization_lp_output, optimization_qubo_output)

            # Calculate optimized JSON with schedules
            optimized_json = optimize_timetable(delayed_json, output_path)

            # Verification: No more conflicts -> again in a valid schedule
            print(optimized_json)
            optimized_data = load_json_file(optimized_json)
            optimized_instance = extract_problem_instance_from_json(optimized_data)

            still_conflicted = detect_conflicts(optimized_instance)

            if still_conflicted:
                print("Optimization was not successful! Conflict count != 0")
                print_conflicts(still_conflicted)
            else:
                print("Optimization was  successful! Conflict count == 0")

        else:
            # No delays or conflicts
            print("\nNo delays or conflicts detected. Schedule is optimal.")




