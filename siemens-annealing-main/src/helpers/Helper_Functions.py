import json

from classes.Line import Line
from classes.RailNetwork import RailNetwork
from classes.Route import Route
from classes.Schedule import ScheduleEntry, Schedule
from classes.Station import Station
from classes.Tau import Tau
from classes.Train import Train
from classes.ProblemInstance import ProblemInstance


def load_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data


def extract_delays(data):
    delays = {}
    trains_data = data.get("trains", [])
    for train_data in trains_data:
        train_id = train_data["id"]
        schedule_data = train_data["schedule"]
        for station_schedule_data in schedule_data:
            station_id = station_schedule_data["station"]
            platform = station_schedule_data["platform"]
            delay = station_schedule_data.get("arrival", 0)  # Assume 0 delay if arrival is not specified
            key = (train_id, station_id, platform)
            delays[key] = delay
    return delays


def extract_max_delays(data):
    max_delays = {}
    trains_data = data.get("trains", [])
    for train_data in trains_data:
        train_id = train_data["id"]
        max_delay = train_data.get("max_delay", 8)  # Assume 5 max delay if not specified
        max_delays[str(train_id)] = max_delay
    return max_delays


def extract_weights(data):
    weights = {}
    trains_data = data.get("trains", [])
    for train_data in trains_data:
        train_id = train_data["id"]
        weight = train_data.get("weight", 0)  # Assume 0 weight if not specified
        weights[train_id] = weight
    return weights


def extract_successor(data):
    successor = {}
    trains_data = data.get("trains", [])
    for train_data in trains_data:
        train_id = train_data["id"]
        schedule_data = train_data["schedule"]
        for i in range(len(schedule_data) - 1):
            curr_station = schedule_data[i]["station"]
            next_station = schedule_data[i + 1]["station"]
            curr_platform = schedule_data[i]["platform"]
            key = (str(train_id), str(curr_station))
            successor[key] = str(next_station)
    return successor


def extract_tau_values(data):
    tau_1 = {}
    tau_2 = {}
    trains_data = data.get("trains", [])
    for train_data in trains_data:
        train_id = train_data["id"]
        schedule_data = train_data["schedule"]
        for i in range(len(schedule_data) - 1):
            curr_station = schedule_data[i]["station"]
            next_station = schedule_data[i + 1]["station"]
            curr_platform = schedule_data[i]["platform"]
            tau_1_key = (str(train_id), str(curr_station), str(next_station))
            tau_2_key = (str(train_id), str(curr_station), str(next_station))
            tau_1_value = schedule_data[i].get("tau_1", 2)  # Assume 0 tau_1 if not specified
            tau_2_value = schedule_data[i].get("tau_2", 3)  # Assume 0 tau_2 if not specified
            tau_1[tau_1_key] = tau_1_value
            tau_2[tau_2_key] = tau_2_value
    return tau_1, tau_2


def convert_minutes_to_time(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return "{:02d}:{:02d}".format(hours, minutes)

# TODO not always 8:00
def create_sigma_out(problem_instance):
    sigma_out = {}
    start_time = 8 * 60  # Start time at 8:00 (in minutes)
    for train in problem_instance.trains:
        schedule = problem_instance.get_schedule(train.train_id)
        num_entries = len(schedule.entries)
        for i, entry in enumerate(schedule.entries):
            station = entry.station
            departure_time = entry.departure
            arrival_time = entry.arrival

            if departure_time is not None:
                hours, minutes = map(int, departure_time.split(':'))
                time = (hours * 60 + minutes) - start_time
                sigma_out[(train.train_id, station)] = time
            else:
                if i == num_entries - 1:  # last station
                    prev_departure = sigma_out.get((train.train_id, schedule.entries[i - 1].station))
                    if prev_departure is not None:
                        sigma_out[(train.train_id, station)] = prev_departure + 3
                    else:
                        sigma_out[(train.train_id, station)] = None
                else:
                    next_arrival = schedule.entries[i + 1].arrival
                    if next_arrival is not None:
                        hours, minutes = map(int, next_arrival.split(':'))
                        time = (hours * 60 + minutes) - start_time
                        sigma_out[(train.train_id, station)] = time
                    else:
                        sigma_out[(train.train_id, station)] = None

    return sigma_out


def extract_trains(data, rail_network):
    stations_data = data.get("stations", [])
    stations = {}
    for station_data in stations_data:
        station_id = station_data.get("id")
        station_name = station_data.get("name")
        stations[station_id] = station_name

    track_lines_data = data.get("track_lines", [])
    track_lines = {}
    for track_line_data in track_lines_data:
        from_station = track_line_data.get("from_station")
        to_station = track_line_data.get("to_station")
        distance = track_line_data.get("distance")
        track_lines[(from_station, to_station)] = distance

    trains_data = data.get("trains", [])
    trains = []
    for train_data in trains_data:
        train_id = train_data.get("id")
        train_name = train_data.get("name")
        train_type = train_data.get("type")
        schedule_data = train_data.get("schedule", [])
        route = []
        for i in range(len(schedule_data) - 1):
            from_station_id = schedule_data[i].get("station")
            to_station_id = schedule_data[i + 1].get("station")
            from_station_name = stations.get(from_station_id)
            to_station_name = stations.get(to_station_id)
            distance = rail_network.get_distance(from_station_name, to_station_name)
            from_platform = schedule_data[i].get("from_platform")
            to_platform = schedule_data[i].get("to_platform")
            line = schedule_data[i].get("line")
            route.append(Route(from_station_id, to_station_id, distance, from_platform, to_platform, line))
        train = Train(train_id, train_name, train_type, route)
        trains.append(train)
    return trains


def extract_routes(data):
    routes = {}
    for train_data in data["trains"]:
        train_id = train_data["id"]
        route = [str(stop["station"]) for stop in train_data["schedule"]]
        routes[str(train_id)] = route

    return routes


def extract_schedules(data):
    schedules_data = data.get("trains", [])
    schedules = []
    for train_data in schedules_data:
        train_id = train_data.get("id")
        schedule_data = train_data.get("schedule", [])
        entries = []
        for stop_data in schedule_data:
            station = stop_data.get("station")
            platform = stop_data.get("platform")
            arrival = stop_data.get("arrival")
            departure = stop_data.get("departure")
            entry = ScheduleEntry(station, arrival, departure, platform)
            entries.append(entry)
        schedule = Schedule(train_id, entries)
        schedules.append(schedule)
    return schedules


def extract_rail_network(data):
    stations_data = data.get("stations", [])
    track_lines_data = data.get("track_lines", [])
    stations = []
    lines = []
    Line.reset_counter()  # Reset the line_id counter
    for station_data in stations_data:
        station_id = station_data.get("id")
        name = station_data.get("name")
        capacity = station_data.get("capacity")
        station = Station(station_id, name, capacity)
        stations.append(station)
    for track_line_data in track_lines_data:
        from_station = track_line_data.get("from_station")
        to_station = track_line_data.get("to_station")
        distance = track_line_data.get("distance")
        capacity = track_line_data.get("capacity")
        line_id = Line.id_counter  # Use the line_id counter as the line_id
        line = Line(line_id, from_station, to_station, distance, capacity)
        lines.append(line)
        Line.id_counter += 1  # Increment the line_id counter
    rail_network = RailNetwork(stations, lines)
    return rail_network


# not in JSON by now
def extract_taus(data):
    tau_same_direction = Tau("same_direction")
    tau_opposite_direction = Tau("opposite_direction")
    return {
        "same_direction": tau_same_direction,
        "opposite_direction": tau_opposite_direction
    }


def extract_problem_instance_from_json(data):
    rail_network = extract_rail_network(data)
    trains = extract_trains(data, rail_network)
    schedules = extract_schedules(data)
    taus = extract_taus(data)

    problem_instance = ProblemInstance(trains, schedules, rail_network, taus)
    return problem_instance


def print_problem_instance(instance):
    print("Trains:")
    for train in instance.trains:
        print(f"Train {train.train_id}: {train.name} ({train.train_type})")
        print("Route:")
        for route in train.route:
            from_station_name = instance.rail_network.get_station_name(route.from_station)
            to_station_name = instance.rail_network.get_station_name(route.to_station)
            print(f"- From Station: {from_station_name}")
            print(f"  To Station: {to_station_name}")
        print()

    print("Schedules:")
    for schedule in instance.schedules:
        print(f"Train: {schedule.train}")
        print("Entries:")
        for entry in schedule.entries:
            print(f"- Station: {entry.station}")
            print(f"  Platform: {entry.platform}")
            print(f"  Arrival: {entry.arrival}")
            print(f"  Departure: {entry.departure}")
        print()

    print("Rail Network:")
    print("Stations:")
    for station in instance.rail_network.stations:
        print(f"- Station ID: {station.station_id}")
        print(f"  Name: {station.name}")
        print(f"  Capacity: {station.capacity}")
        print("  Platforms:")
        for platform in station.platforms:
            print(f"    Platform ID: {platform.platform_id}")
            print(f"    Name: {platform.name}")
        print()

    print("Lines:")
    for line in instance.rail_network.lines:
        print(f"- Line ID: {line.line_id}")
        print(f"  From Station: {line.from_station}")
        print(f"  To Station: {line.to_station}")
        print(f"  Distance: {line.distance}")
        print(f"  Capacity: {line.capacity}")
    print()

    print("Tau Values:")
    for key, value in instance.taus.items():
        print(f"{key}: {value}")
    print("-" * 30)