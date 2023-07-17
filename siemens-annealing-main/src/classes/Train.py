class Train:
    def __init__(self, train_id, name, train_type, route):
        self.train_id = train_id
        self.name = name
        self.train_type = train_type
        self.route = route
        self.priority = self.get_priority()
        self.speed = self.get_speed()

    def get_priority(self):
        if self.train_type == 'express':
            return 2
        elif self.train_type == 'city':
            return 1
        else:
            return 0  # Set a default priority if the type is unknown

    def get_speed(self):
        if self.train_type == 'express':
            return 80
        elif self.train_type == 'city':
            return 80

    def get_route(self):
        print(self.route)
        self.route

