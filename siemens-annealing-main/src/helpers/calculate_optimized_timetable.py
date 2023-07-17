import json
import os
import datetime


def optimize_timetable(delayed_timetable_file, optimization_values_file):
    # Load the delayed timetable and optimization values from the JSON files
    with open(delayed_timetable_file) as delayed_file:
        delayed_timetable = json.load(delayed_file)

    with open(optimization_values_file) as optimization_file:
        optimization_values = json.load(optimization_file)

    # Check if the optimization result for "Optimization with QUBO" is present
    if 'Optimization with QUBO' in optimization_values['Delays']['optimization_output']:
        optimization_result = optimization_values['Delays']['optimization_output']['Optimization with QUBO']

        # Create a copy of the delayed timetable for modifications
        optimized_timetable = delayed_timetable.copy()

        # Iterate over each optimization value and update the departure and arrival times accordingly
        for key, value in optimization_result.items():
            parts = key.split('_', 1)
            if len(parts) < 2:
                continue

            train_id = int(parts[1].split('_')[0])
            station_id = int(parts[1].split('_')[1])

            if value != 0:
                # Find the train and station in the optimized timetable
                train = next((train for train in optimized_timetable['trains'] if train['id'] == train_id), None)
                if train:
                    schedule = train['schedule']
                    for entry in schedule:
                        if entry['station'] == station_id:
                            # Update the departure and arrival times by the value of the optimization
                            if entry['departure'] is not None:
                                entry['departure'] = add_minutes_to_time(entry['departure'], value)
                            if entry['arrival'] is not None:
                                entry['arrival'] = add_minutes_to_time(entry['arrival'], value)
                            break

        # Extract the number from the delayed timetable file path
        num = extract_number_from_filename(delayed_timetable_file)

        # Generate the new file name for the optimized timetable
        optimized_timetable_file = f"timetables/{num}_optimized_timetable.json"

        # Save the optimized timetable in the new JSON file
        with open(optimized_timetable_file, 'w') as output_file:
            json.dump(optimized_timetable, output_file, indent=4)

        return optimized_timetable_file
    else:
        print("No optimization results found for 'Optimization with QUBO'.")


# Helper function to add minutes to a time string in 'HH:MM' format
def add_minutes_to_time(time_str, minutes):
    time = datetime.datetime.strptime(time_str, "%H:%M")
    time += datetime.timedelta(minutes=minutes)
    return time.strftime("%H:%M")


# Helper function to extract the number from a file name
def extract_number_from_filename(filename):
    basename = os.path.basename(filename)
    num_str = ''.join(filter(str.isdigit, basename))
    return int(num_str)
