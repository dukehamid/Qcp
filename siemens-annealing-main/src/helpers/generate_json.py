import os
import random
import json

def generate_initial_timetable(num_stations=None, num_trains=None, d_max=None):
    qubits = 0

    while qubits < 96 or qubits > 120:
        while qubits < 12:
            if num_stations is None:
                num_stations = random.randint(3, 10)  # Random number of stations between 3 and 10
            if num_trains is None:
                num_trains = random.randint(3, 6)  # Random number of trains between 2 and 6

            qubits = (num_stations - 1) * num_trains

        if d_max is None:
            d_max = random.randint(1, 5)  # Random value for d_max between 1 and 5

        qubits = (num_stations - 1) * num_trains * (d_max + 1)

    # Stations
    stations = []
    station_names = [f"Station {i}" for i in range(101, 101 + num_stations)]
    capacities = [random.choice([1, 2, 3]) for _ in range(num_stations)]
    for i in range(num_stations):
        station = {"id": 101 + i, "name": station_names[i], "capacity": capacities[i]}
        stations.append(station)

    # Track Lines
    track_lines = []
    for i in range(num_stations - 1):
        from_station = 101 + i
        to_station = 101 + i + 1
        distance = round(random.uniform(3, 15), 2)
        line = {"from_station": from_station, "to_station": to_station, "distance": distance, "capacity": 1}
        track_lines.append(line)

    # Trains
    trains = []
    train_names = [f"Train {i + 1}" for i in range(num_trains)]
    departure_time = random.randint(6, 19) * 60  # Initial departure time in minutes
    time_window = 2 * 60  # Time window for schedules in minutes
    for i in range(num_trains):
        train_type = random.choice(["express", "city"])
        schedule = []
        start_station = random.choice([101 + j for j in range(num_stations)])  # Randomly select the starting station
        start_index = start_station - 101
        direction = 1 if start_station == 101 else (-1 if start_station == 105 else random.choice([-1, 1])) # Direction: 1 for forward, -1 for backward
        stations_order = list(range(start_index, num_stations)) if direction == 1 else list(range(start_index, -1, -1))
        for j in stations_order:
            station_id = 101 + j
            platform = random.randint(1, 3)
            arrival = None
            departure = None
            if j == start_index:
                departure = format_time(departure_time)
            elif j == num_stations - 1:
                arrival = format_time(departure_time + random.randint(10, 30))  # Add random minutes to departure time
                departure = None
            else:
                if direction == 1:
                    if random.random() < 0.5 or j == num_stations - 2:  # Probability of not stopping at the station or last but one station
                        departure_time += random.randint(3, 5)  # Add waiting time at the station and platform
                        departure = format_time(departure_time)
                        continue
                    arrival_time = departure_time + random.randint(5, 20)  # Add random minutes to departure time
                    arrival = format_time(arrival_time)
                    departure_time = arrival_time + random.randint(3, 5)  # Add waiting time at the station and platform
                    departure = format_time(departure_time)
                else:
                    if random.random() < 0.5 or j == num_stations - 2:  # Probability of not stopping at the station or last but one station
                        departure_time -= random.randint(3, 5)  # Subtract waiting time at the station and platform
                        departure = format_time(departure_time)
                        continue
                    arrival_time = departure_time - random.randint(5, 20)  # Subtract random minutes from departure time
                    arrival = format_time(arrival_time)
                    departure_time = arrival_time - random.randint(3, 5)  # Subtract waiting time at the station and platform
                    departure = format_time(departure_time)
            schedule.append({"station": station_id, "platform": platform, "arrival": arrival, "departure": departure})
        train = {"id": 10 + i, "name": train_names[i], "type": train_type, "schedule": schedule}
        trains.append(train)

    # Create JSON data
    data = {
        "stations": stations,
        "track_lines": track_lines,
        "trains": trains
    }

    # Save JSON data to a file
    file_num = get_next_file_number("timetables/", "_initial_timetable")
    file_name = f"{file_num}_initial_timetable.json"
    file_path = f"timetables/{file_name}"
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Generated initial timetable: {file_name}")
    return qubits, file_path, d_max


def format_time(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def get_next_file_number(folder_path, file_suffix):
    files = [file for file in os.listdir(folder_path) if file.endswith(".json")]
    existing_numbers = []
    for file in files:
        try:
            number = int(file.split("_")[0])
            existing_numbers.append(number)
        except ValueError:
            pass
    return max(existing_numbers) + 1 if existing_numbers else 1
