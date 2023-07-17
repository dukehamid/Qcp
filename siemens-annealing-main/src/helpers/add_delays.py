import json
import random
import os


def generate_delayed_schedules(json_file, max_delay):
    with open(json_file) as file:
        data = json.load(file)

    for train in data['trains']:
        schedule = train['schedule']
        for entry in schedule:
            delay = random.randint(0, max_delay)
            if entry['arrival']:
                entry['arrival'] = add_delay(entry['arrival'], delay)
            if entry['departure']:
                entry['departure'] = add_delay(entry['departure'], delay)

    directory = "timetables"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = os.path.basename(json_file)
    file_name_without_ext = os.path.splitext(file_name)[0]
    new_file_name = f"{file_name_without_ext}_delayed.json"
    output_path = os.path.join(directory, new_file_name)
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=2)

    return output_path


def add_delay(time, delay):
    hours, minutes = map(int, time.split(':'))
    total_minutes = hours * 60 + minutes

    delayed_minutes = total_minutes + delay

    delayed_hours = delayed_minutes // 60
    delayed_minutes %= 60
    return f'{delayed_hours:02d}:{delayed_minutes:02d}'
