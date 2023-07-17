import datetime
import json

import matplotlib.pyplot as plt
import os

def plot_train_schedule(train_data, station_data, json_file_name):
    # Extract stations -> for y-axis
    station_names = {station['id']: station['name'] for station in station_data}
    station_capacities = {station['id']: station['capacity'] for station in station_data}

    # Find earliest and latest time -> for x-axis
    earliest_time = None
    latest_time = None

    for train in train_data:
        schedule = train['schedule']
        for entry in schedule:
            departure = entry['departure']
            arrival = entry['arrival']

            if departure is not None:
                time = datetime.datetime.strptime(departure, '%H:%M')
                if earliest_time is None or time < earliest_time:
                    earliest_time = time
                if latest_time is None or time > latest_time:
                    latest_time = time

            if arrival is not None:
                time = datetime.datetime.strptime(arrival, '%H:%M')
                if earliest_time is None or time < earliest_time:
                    earliest_time = time
                if latest_time is None or time > latest_time:
                    latest_time = time

    stations = list(station_names.values())

    start_time = earliest_time

    time_range = []
    current_time = start_time

    while current_time <= latest_time:
        time_range.append(current_time)
        current_time += datetime.timedelta(minutes=15)

    plt.figure(figsize=(10, 6))
    for train in train_data:
        schedule = train['schedule']
        time_points = []
        station_indices = []

        for entry in schedule:
            departure = entry['departure']
            arrival = entry['arrival']

            if departure is not None:
                time = datetime.datetime.strptime(departure, '%H:%M')
                if arrival != departure:  # Filter out non-stop points
                    time_points.append(time)
                    station_id = entry['station']
                    station_name = station_names.get(station_id)
                    if station_name in stations:
                        station_indices.append(stations.index(station_name))

            if arrival is not None:
                time = datetime.datetime.strptime(arrival, '%H:%M')
                if arrival != departure:  # Filter out non-stop points
                    time_points.append(time)
                    station_id = entry['station']
                    station_name = station_names.get(station_id)
                    if station_name in stations:
                        station_indices.append(stations.index(station_name))

        sorted_points = sorted(zip(time_points, station_indices))
        sorted_times, sorted_indices = zip(*sorted_points)

        plt.plot(sorted_times, sorted_indices, marker='o', label=train['name'])

    last_arrival_time = max(sorted_times) if sorted_times else None
    if last_arrival_time is not None:
        last_arrival_time_scalar = last_arrival_time.timestamp()
        plt.axhline(y=sorted_indices[-1], xmin=0, xmax=last_arrival_time_scalar, color='gray', linestyle='--')

    plt.yticks(range(len(stations)),
               [f"{station}\n(Station Capacity: {station_capacities[station_id]})" for station_id, station in
                station_names.items()])

    plt.xticks(time_range, [time.strftime('%H:%M') for time in time_range])
    plt.xlabel('Time')
    plt.ylabel('Stations')

    # Add station capacities
    for index, station_id in enumerate(stations):
        capacity = station_capacities.get(station_id)
        if capacity:
            plt.text(-0.15, index, f"Station Capacity: {capacity}", ha='right', va='center', fontsize=8)

    plt.title(f'Schedules ({json_file_name})')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()

    # Save the plot image
    directory = "plots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    output_path = os.path.join(directory, f"plot_{json_file_name}.png")
    plt.savefig(output_path)
    plt.close()


def plot_all_schedules():
    directory = 'timetables'

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(directory, filename)
            with open(json_file_path) as json_file:
                data = json.load(json_file)
                train_data = data['trains']
                station_data = data['stations']
                file_name_without_ext = os.path.splitext(filename)[0]
                plot_train_schedule(train_data, station_data, file_name_without_ext)
