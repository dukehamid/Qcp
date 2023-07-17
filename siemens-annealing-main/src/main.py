from conflict_detection.Conflicts import detect_conflicts, print_conflicts
from conflict_detection.Delays import detect_delays
from helpers.calculate_optimized_timetable import optimize_timetable
from helpers.plot_railnetwork import plot_all_railnetworks
from helpers.plot_schedules import plot_all_schedules
from optimization.lp_represenation import optimize_schedule_lp
from helpers.bundle_optimization_outputs import save_optimization_output
from optimization.qubo import optimize_schedule_qubo
from helpers.Helper_Functions import extract_problem_instance_from_json, load_json_file, print_problem_instance, \
    extract_max_delays, extract_successor, extract_tau_values, create_sigma_out, extract_routes


# load data from JSON files and save it to problem_instance
initial_json = "timetables/1_initial_timetable.json"
initial_data = load_json_file(initial_json)
initial_instance = extract_problem_instance_from_json(initial_data)
#print("Initial Instance")
#print_problem_instance(initial_instance)

delayed_json = "timetables/1_delay_timetable.json"
delay_data = load_json_file(delayed_json)
problem_instance = extract_problem_instance_from_json(delay_data)
#print("Delayed Instance")
#print_problem_instance(problem_instance)

plot_all_railnetworks()
plot_all_schedules()

# Detect Delays
print("\nDelays:")
delayed, delay_amounts = detect_delays(initial_instance, problem_instance)
#print(delay_amounts)

# if Delay detected, check for conflicts
if delayed:
    print("\nDelay detected! Checking for conflicts...")
    sigma_out = create_sigma_out(problem_instance)  # Timetable time of leaving
    conflicts = detect_conflicts(problem_instance)
    #print_conflicts(conflicts)

    if conflicts:
        print("\nConflict detected! Starting with optimization...")

        J = [str(train.train_id) for train in problem_instance.trains]  # Set of trains
        S = extract_routes(delay_data)  # Set of stations for each train
        d_u = {(str(j), str(s)): delay_amounts[(j, s)] for j, s in delay_amounts}  # Unavoidable delay
        d_max = extract_max_delays(delay_data)  # Maximum delay
        w = {str(train.train_id): train.priority for train in problem_instance.trains}  # Weights reflecting the trains priority
        successor = extract_successor(delay_data)  # Next station block
        tau_1, tau_2 = extract_tau_values(delay_data)  # Minimal time for train to give way to another train in the same/opposite direction
        sigma_out_par = {(str(j), str(s)): sigma_out[(j, s)] for j, s in sigma_out}
        M = 1000  # Large positive number (big-M method)

        # Optimization with lp
        print("Optimizing with LP:")
        optimization_lp_output = optimize_schedule_lp(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par, M)
        print("-" * 30)

        #print('MATRIX')
        #mat = generate_qubo_matrix(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par, M)

        # Optimization with qubo
        print("Optimizing with QUBO:")
        optimization_qubo_output = optimize_schedule_qubo(J, S, d_u, d_max, w, successor, tau_1, tau_2, sigma_out_par, M)
        print("-" * 30)

        # Bundle optimization values in JSON file
        output_path = save_optimization_output(initial_json, delayed, delay_amounts, conflicts, optimization_lp_output,optimization_qubo_output)

        # Calculate optimized timetable
        optimized_path = optimize_timetable(delayed_json, output_path)

        # Verification: No more conflicts -> again in a valid schedule
        optimized_json = optimized_path
        #print(optimized_json)
        optimized_data = load_json_file(optimized_json)
        optimized_instance = extract_problem_instance_from_json(optimized_data)
        #print_problem_instance(optimized_instance)

        plot_all_railnetworks()
        plot_all_schedules()

       # still_conflicted = detect_conflicts(optimized_instance)

        #if still_conflicted:
        #    print("Optimization was not successful! Conflict count != 0")
        #    print_conflicts(still_conflicted)
        #else:
        #    print("Optimization was  successful! Conflict count == 0")

else:
    # No delays or conflicts
    print("\nNo delays or conflicts detected. Schedule is optimal.")
