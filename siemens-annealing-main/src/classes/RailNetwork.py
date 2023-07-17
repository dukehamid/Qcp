class Connection:
    def __init__(self, station, line):
        self.station = station
        self.line = line


class RailNetwork:
    def __init__(self, stations, lines):
        self.stations = stations
        self.lines = lines
        self.connections = self.create_connections()

    def create_connections(self):
        connections = []
        for station in self.stations:
            for line in self.lines:
                if station.station_id == line.from_station or station.station_id == line.to_station:
                    connection = Connection(station, line)
                    connections.append(connection)
        return connections

    def get_station(self, station_id):
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None

    def get_station_name(self, station_id):
        for station in self.stations:
            if station.station_id == station_id:
                return station.name
        return None

    def get_distance(self, from_station, to_station):
        for line in self.lines:
            if line.from_station == from_station and line.to_station == to_station:
                return line.distance
            elif line.from_station == to_station and line.to_station == from_station:
                return line.distance
        return None

    def get_line_stations(self, line_id):
        line_stations = []
        for connection in self.connections:
            if connection.line.line_id == line_id:
                line_stations.append(connection.station.station_id)
        return line_stations



