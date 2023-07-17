# Tau can have different types -> it is a time frame for a certain setting
def calculate_value(tau_type):
    if tau_type == "same_direction":
        return 2
    elif tau_type == "opposite_direction":
        return 3
    else:
        raise ValueError("Invalid Tau type: {}".format(tau_type))


class Tau:
    def __init__(self, tau_type):
        self.tau_type = tau_type
        self.value = calculate_value(tau_type)

    def __str__(self):
        return str(self.value)
