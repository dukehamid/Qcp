from datetime import datetime


def detect_delays(initial_instance, problem_instance):
    delay_amounts = {}
    delayed = False

    # Iterate over each train in the problem instance
    for train in problem_instance.trains:
        # Get the initial schedule and current schedule for the train
        initial_schedule = initial_instance.get_schedule(train.train_id)
        current_schedule = problem_instance.get_schedule(train.train_id)

        previous_delay = 0

        # Iterate over each station in the schedule entries
        for i in range(len(initial_schedule.entries)):
            station = current_schedule.entries[i].station

            initial_departure_str = initial_schedule.entries[i].departure
            current_departure_str = current_schedule.entries[i].departure

            # Check if both initial and current departure times exist
            if initial_departure_str is not None and current_departure_str is not None:
                # Convert departure times to datetime objects
                initial_departure = datetime.strptime(initial_departure_str, "%H:%M")
                current_departure = datetime.strptime(current_departure_str, "%H:%M")

                # Calculate delay amount in minutes
                if initial_departure != current_departure:
                    delay_amount = int((current_departure - initial_departure).total_seconds() / 60)
                    delayed = True
                else:
                    delay_amount = 0

                # Store the delay amount for the train at the station
                delay_amounts[(train.train_id, station)] = delay_amount
                print(f"Delay for Train {train.train_id} at Station {station}: {delay_amount} minutes")

                previous_delay = delay_amount
            else:
                # If departure time is missing, use the previous delay amount
                delay_amounts[(train.train_id, station)] = previous_delay
                print(f"Delay for Train {train.train_id} at Station {station}: {previous_delay} minutes")

    return delayed, delay_amounts
