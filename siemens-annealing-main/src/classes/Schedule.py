class ScheduleEntry:
    def __init__(self, station, arrival, departure, platform):
        self.station = station
        self.arrival = arrival
        self.departure = departure
        self.platform = platform

    def create_entries(stations, arrivals, departures, platforms):
        entries = []
        for station, arrival, departure, platform in zip(stations, arrivals, departures, platforms):
            entry = ScheduleEntry(station, arrival, departure, platform)
            entries.append(entry)
        return entries

    def __str__(self):
        return f"Station: {self.station}, Arrival: {self.arrival}, Departure: {self.departure}, Platform: {self.platform}"


class Schedule:
    def __init__(self, train, entries):
        self.train = train
        self.entries = entries

    def __str__(self):
        entry_str = ", ".join(str(entry) for entry in self.entries)
        return f"Train: {self.train}, Entries: {entry_str}"

    def get_entry_by_station(self, station):
        for entry in self.entries:
            if entry.station == station:
                return entry
        return None
