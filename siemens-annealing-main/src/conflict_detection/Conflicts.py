def detect_conflicts(problem_instance):
    conflicts = []

    num_lines = len(problem_instance.rail_network.lines)
    num_stations = len(problem_instance.rail_network.stations)

    # Check for station capacity conflicts
    time_intervals_station = remove_duplicates_intervals(get_time_intervals(problem_instance, "stations"))

    for station_id in range(101, 100 + num_stations + 1):
        for time_interval in time_intervals_station:
            trains_at_station = problem_instance.get_trains_at_station(station_id, time_interval)
            num_trains_at_station = len(trains_at_station)

            if num_trains_at_station > problem_instance.get_station_capacity(station_id):
                conflict = {
                    'trains': trains_at_station,
                    'time_interval': time_interval,
                    'conflict_type': 'capacity_station',
                    'station': station_id
                }
                conflicts.append(conflict)

    # Check for platform capacity conflicts
    time_intervals_platform = remove_duplicates_intervals(get_time_intervals(problem_instance, "platforms"))

    for station_id in range(101, 100 + num_stations + 1):
        station_capacity = problem_instance.get_station_capacity(station_id)

        for platform_id in range(1, station_capacity + 1):
            for time_interval in time_intervals_platform:
                trains_on_platform = problem_instance.get_trains_on_platform(platform_id, station_id, time_interval)
                num_trains_on_platform = len(trains_on_platform)

                if num_trains_on_platform > 1:
                    conflict = {
                        'trains': trains_on_platform,
                        'time_interval': time_interval,
                        'conflict_type': 'capacity_platform',
                        'station': station_id,
                        'platform': platform_id
                    }
                    conflicts.append(conflict)

    # Check for line capacity conflicts
    time_intervals_lines = get_time_intervals(problem_instance, "lines")

    for line_id in range(num_lines):
        for time_interval in time_intervals_lines:
            intersection_trains = problem_instance.find_line_intersection_trains(line_id, time_interval)

            if len(intersection_trains) > 1:
                conflict = {
                    'trains': intersection_trains,
                    'time_interval': time_interval,
                    'conflict_type': 'capacity_line',
                    'line': line_id
                }
                conflicts.append(conflict)

    conflicts = remove_duplicates_conflicts(conflicts)
    print("Number of conflicts:", len(conflicts))
    num_capacity_station = count_conflicts_by_type(conflicts, 'capacity_station')
    print("Number of capacity_station conflicts:", num_capacity_station)
    num_capacity_platform = count_conflicts_by_type(conflicts, 'capacity_platform')
    print("Number of capacity_platform conflicts:", num_capacity_platform)
    num_capacity_line = count_conflicts_by_type(conflicts, 'capacity_line')
    print("Number of capacity_line conflicts:", num_capacity_line)
    print("-" * 30)
    return conflicts

def remove_duplicates_conflicts(conflicts):
    unique_conflicts = []
    conflict_set = set()

    for conflict in conflicts:
        conflict_str = str(conflict)

        if conflict_str not in conflict_set:
            conflict_set.add(conflict_str)
            unique_conflicts.append(conflict)

    return unique_conflicts



def remove_duplicates_intervals(intervals):
    unique_intervals = []
    seen_intervals = set()

    for interval in intervals:
        if interval not in seen_intervals:
            unique_intervals.append(interval)
            seen_intervals.add(interval)

    return unique_intervals


def count_conflicts_by_type(conflicts, conflict_type):
    sub_conflicts = [conflict for conflict in conflicts if conflict['conflict_type'] == conflict_type]
    return len(sub_conflicts)


def get_time_intervals(problem_instance, typ):
    time_intervals = []

    for train in problem_instance.trains:
        schedule = problem_instance.get_schedule(train.train_id)
        if typ == "all":
            intervals = get_train_time_intervals(schedule)
        elif typ == "stations":
            intervals = get_train_station_time_intervals(schedule)
        elif typ == "platforms":
            intervals = get_train_station_time_intervals(schedule)
        elif typ == "lines":
            intervals = get_train_line_time_intervals(schedule)

        time_intervals.extend(intervals)

    return time_intervals


def get_train_line_time_intervals(schedule):
    intervals = []

    num_entries = len(schedule.entries)
    for i in range(num_entries):
        entry = schedule.entries[i]
        if entry.departure is not None:
            next_entry = schedule.entries[i + 1]
            interval_l = (entry.departure, next_entry.arrival)
            intervals.append(interval_l)

    return intervals


def get_train_station_time_intervals(schedule):
    intervals = []

    num_entries = len(schedule.entries)
    for i in range(num_entries):
        entry = schedule.entries[i]
        if entry.departure is not None:
            if i == 0:  # First station
                interval_s = (entry.departure, entry.departure)
                intervals.append(interval_s)

        if entry.arrival is not None:
            if i == num_entries - 1:  # Last station

                interval_s = (entry.arrival, entry.arrival)
                intervals.append(interval_s)

            else:
                interval_s = (entry.arrival, entry.departure)
                intervals.append(interval_s)

    return intervals


def get_train_time_intervals(schedule):
    intervals = []

    num_entries = len(schedule.entries)
    for i in range(num_entries):
        entry = schedule.entries[i]
        if entry.departure is not None:
            if i == 0:  # First station
                interval_s = (entry.departure, entry.departure)
                intervals.append(interval_s)

                next_entry = schedule.entries[i + 1]
                interval_l = (entry.departure, next_entry.arrival)
                intervals.append(interval_l)

        if entry.arrival is not None:
            if i == num_entries - 1:  # Last station

                prev_entry = schedule.entries[i - 1]
                interval_l = (prev_entry.departure, entry.arrival)
                intervals.append(interval_l)

                interval_s = (entry.arrival, entry.arrival)
                intervals.append(interval_s)

            else:
                # next_entry = schedule.entries[i + 1]
                interval_s = (entry.arrival, entry.departure)
                intervals.append(interval_s)

    return intervals


def intervals_overlap(interval1, interval2):
    start1, end1 = interval1
    start2, end2 = interval2

    if start1 is None:
        start1 = start2
    if end1 is None:
        end1 = end2
    if start2 is None:
        start2 = start1
    if end2 is None:
        end2 = end1

    return start1 <= end2 and end1 >= start2


def time_to_minutes(time):
    hours, minutes = time.split(":")
    return int(hours) * 60 + int(minutes)


def time_to_clock(time):
    hours = time // 60
    minutes = time % 60
    return f"{hours:02d}:{minutes:02d}"


def print_conflicts(conflicts):
    if len(conflicts) == 0:
        print("No conflicts detected.")
        return

    print("Conflicts detected:")
    for conflict in conflicts:
        print_conflict_details(conflict)


def print_conflict_details(conflict):
    trains = conflict["trains"]
    time_interval = conflict.get("time_interval", "Unknown")
    conflict_type = conflict["conflict_type"]

    print(f"Time Interval: {time_interval}")
    print(f"Conflict Type: {conflict_type}")

    if conflict_type == "capacity_station":
        station = conflict.get("station", "Unknown")
        print(f"Conflict at Station: {station}")
    elif conflict_type == "capacity_line":
        line = conflict.get("line", "Unknown")
        print(f"Conflict on Line: {line}")
    elif conflict_type == "capacity_platform":
        station = conflict.get("station", "Unknown")
        platform = conflict.get("platform", "Unknown")
        print(f"Conflict at Station: {station}")
        print(f"Conflict on Platform: {platform}")

    print("Conflicting Trains:")
    for train in trains:
        print(train)

    print("-" * 30)

