from conflict_detection.Conflicts import intervals_overlap
from datetime import datetime

class ProblemInstance:
    def __init__(self, trains, schedules, rail_network, taus):
        self.trains = trains
        self.schedules = schedules
        self.rail_network = rail_network
        self.taus = taus

    def get_schedule(self, train_id):
        for schedule in self.schedules:
            if schedule.train == train_id:
                return schedule
        return None

    def find_train_by_id(self, train_id):
        for train in self.trains:
            if train.train_id == train_id:
                return train
        return None

    def find_train_by_name(self, train_name):
        for train in self.trains:
            if train.name == train_name:
                return train
        return None

    def get_tau_value(self, tau_type):
        for tau in self.taus:
            if tau.tau_type == tau_type:
                return tau.value
        raise ValueError("Invalid Tau type: {}".format(tau_type))

    def get_station_capacity(self, station_id):
        for station in self.rail_network.stations:
            if station.station_id == station_id:
                return station.capacity
        return 0

    def get_trains_on_line(self, line_id, time_interval):
        trains_on_line = []

        # Check which stations are enclosed by this line
        line_stations = self.rail_network.get_line_stations(line_id)

        # Check which trains have this route
        for train in self.trains:
            train_schedule = self.get_schedule(train.train_id)
            if train_schedule is not None:
                for i in range(len(train_schedule.entries) - 1):
                    entry1 = train_schedule.entries[i]
                    entry2 = train_schedule.entries[i + 1]

                    station1 = entry1.station
                    station2 = entry2.station

                    if station1 in line_stations and station2 in line_stations:
                        departure_time = entry1.departure
                        arrival_time = entry2.arrival

                        # Check if the time interval overlaps with the departure and arrival times
                        if intervals_overlap((departure_time, arrival_time), time_interval):
                            trains_on_line.append(train.train_id)
                            break

        return trains_on_line

    def find_line_intersection_trains(self, line_id, time_interval):
        line_stations = self.rail_network.get_line_stations(line_id)
        trains_on_line = self.get_trains_on_line(line_id, time_interval)
        intersection_trains = []

        for i in range(len(trains_on_line)):
            for j in range(i + 1, len(trains_on_line)):
                train_id1 = trains_on_line[i]
                train_id2 = trains_on_line[j]

                train_schedule1 = self.get_schedule(train_id1)
                train_schedule2 = self.get_schedule(train_id2)

                if train_schedule1 is not None and train_schedule2 is not None:
                    schedule_entries1 = train_schedule1.entries
                    schedule_entries2 = train_schedule2.entries

                    for k in range(len(schedule_entries1) - 1):
                        entry1 = schedule_entries1[k]
                        entry2 = schedule_entries1[k + 1]

                        station1 = entry1.station
                        station2 = entry2.station

                        if station1 in line_stations and station2 in line_stations:
                            departure_time1 = self.time_to_float(entry1.departure)
                            arrival_time1 = self.time_to_float(entry2.arrival)

                            interval1 = (departure_time1, arrival_time1)

                            for m in range(len(schedule_entries2) - 1):
                                entry3 = schedule_entries2[m]
                                entry4 = schedule_entries2[m + 1]

                                station3 = entry3.station
                                station4 = entry4.station

                                if station3 in line_stations and station4 in line_stations:
                                    departure_time2 = self.time_to_float(entry3.departure)
                                    arrival_time2 = self.time_to_float(entry4.arrival)

                                    interval2 = (departure_time2, arrival_time2)

                                    if intervals_overlap(interval1, interval2):
                                        common_interval = (
                                            max(interval1[0], interval2[0]),
                                            min(interval1[1], interval2[1])
                                        )

                                        time_interval_start = self.time_to_float(time_interval[0])
                                        time_interval_end = self.time_to_float(time_interval[1])

                                        if time_interval_start <= common_interval[0] <= time_interval_end or \
                                                time_interval_start <= common_interval[1] <= time_interval_end:
                                            intersection_trains.append(train_id1)
                                            intersection_trains.append(train_id2)

        return intersection_trains

    # Check which trains are at the station
    def get_trains_at_station(self, station_id, time_interval):
        trains_at_station = []
        for train in self.trains:
            train_schedule = self.get_schedule(train.train_id)
            if train_schedule is not None:
                for schedule_entry in train_schedule.entries:
                    if schedule_entry.station == station_id:
                        if schedule_entry.arrival is None:
                            if intervals_overlap((schedule_entry.departure, schedule_entry.departure), time_interval):
                                trains_at_station.append(train.train_id)
                                break
                        elif schedule_entry.departure is None:
                            if intervals_overlap((schedule_entry.arrival, schedule_entry.arrival), time_interval):
                                trains_at_station.append(train.train_id)
                                break
                        else:
                            if intervals_overlap((schedule_entry.arrival, schedule_entry.departure), time_interval):
                                trains_at_station.append(train.train_id)
                                break
        return trains_at_station

    # Check which trains are on the platform
    def get_trains_on_platform(self, platform_id, station_id, time_interval):
        trains_on_platform = []
        for train in self.trains:
            train_schedule = self.get_schedule(train.train_id)
            if train_schedule is not None:
                for schedule_entry in train_schedule.entries:
                    if schedule_entry.station == station_id and schedule_entry.platform == platform_id:
                        if schedule_entry.arrival is None:
                            if intervals_overlap((schedule_entry.departure, schedule_entry.departure), time_interval):
                                trains_on_platform.append(train.train_id)
                                break
                        elif schedule_entry.departure is None:
                            if intervals_overlap((schedule_entry.arrival, schedule_entry.arrival), time_interval):
                                trains_on_platform.append(train.train_id)
                                break
                        else:
                            if intervals_overlap((schedule_entry.arrival, schedule_entry.departure), time_interval):
                                trains_on_platform.append(train.train_id)
                                break
        return trains_on_platform

    def time_to_float(self, time_string):
        time = datetime.strptime(time_string, '%H:%M')
        return time.hour + time.minute / 60.0
