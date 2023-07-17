# Route(consists of expected arrival + platform) != Schedule
class Route:
    def __init__(self, from_station, to_station, distance, from_platform, to_platform, line):
        self.from_station = from_station
        self.to_station = to_station
        self.distance = distance
        self.from_platform = from_platform
        self.to_platform = to_platform
        self.line = line
