from classes.Platform import Platform


class Station:
    def __init__(self, station_id, name, capacity):
        self.station_id = station_id
        self.name = name
        self.capacity = capacity
        self.platforms = []

        for platform_id in range(1, capacity + 1):
            platform = Platform(platform_id, station_id, f"Platform {platform_id}")
            self.platforms.append(platform)

    def get_station_name(self):
        return self.name

    def get_station_id(self):
        return self.station_id


