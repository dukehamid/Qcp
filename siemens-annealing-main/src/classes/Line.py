class Line:
    id_counter = 0

    def __init__(self, line_id, from_station, to_station, distance, capacity):
        self.line_id = line_id
        self.from_station = from_station
        self.to_station = to_station
        self.distance = distance
        self.capacity = capacity

    @staticmethod
    def reset_counter():
        Line.id_counter = 0
