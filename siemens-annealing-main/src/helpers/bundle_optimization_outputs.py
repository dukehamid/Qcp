import os
import re
import json

def save_optimization_output(initial_json, delayed, delay_amounts, conflicts, optimization_lp_output, optimization_qubo_output):
    # Add optimization outputs to the output dictionary
    delay_amounts = {str(key): value for key, value in delay_amounts.items()}
    output = {
        "Delays": {
            "delayed": delayed,
            "delay_amounts": delay_amounts,
            "conflicts": conflicts,
            "optimization_output": {
                "Optimization with LP": optimization_lp_output,
                "Optimization with QUBO": optimization_qubo_output
            }
        }
    }

    # Extract number from the input JSON filename
    match = re.search(r'\d+', initial_json)
    if match:
        number = match.group()
    else:
        number = 'unknown'

    # Construct the output JSON filename
    output_filename = f"{number}_optimization_values.json"
    output_directory = os.path.dirname("optimization_values/")
    output_path = os.path.join(output_directory, output_filename)

    # Save the output dictionary to the desired JSON file
    with open(output_path, 'w') as file:
        json.dump(output, file, indent=4)

    return output_path
