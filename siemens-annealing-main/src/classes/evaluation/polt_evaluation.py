import matplotlib.pyplot as plt


def calculate_qubits(station_count, num_trains, delay_max):
    qubits = (station_count - 1) * num_trains * (delay_max + 1)
    return qubits


def evaluate(best_result, our_result):
    evaluation = best_result / our_result
    return evaluation


def main():
    num_stations = 2
    num_trains = 3
    delay_max = 7

    best_result = 100.0
    our_result = 80.0

    # Generate a list of total qubits
    total_qubits = []
    for i in range(2, 10):
        qubits = calculate_qubits(num_stations, num_trains, delay_max) + i
        total_qubits.append(qubits)

    # Generate a list of evaluation scores with more data points
    evaluation_score = [0.1,0.3]


    # Synchronize the lists of total qubits and evaluation scores
    data = list(zip(total_qubits, evaluation_score))

    # Sort the data based on the total qubits in ascending order
    data.sort(key=lambda x: x[0])



    # Plotting the chart
    plt.plot(total_qubits, evaluation_score, marker='o')
    plt.title("Quantum Annealing Evaluation")
    plt.xlabel("Total Qubits")
    plt.ylabel("Approx. Ratio")
    plt.grid(True)
    plt.show()

