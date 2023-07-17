import matplotlib.pyplot as plt

qubits = [94, 114, 206]  # List of qubits
approx_ratio = [0.5, 0.75, 0.9]  # List of corresponding Approx.Ratio

# Plotting the chart
plt.plot(qubits, approx_ratio, marker='o', linestyle='-', color='blue')

# Customizing the chart
plt.xlabel('Number of Qubits')
plt.ylabel('Approx.Ratio')
plt.title('Approx.Ratio vs Number of Qubits')
plt.ylim(0.0, 1.0)  # Set the y-axis limits

plt.savefig('plot.png')  # Change the filename and extension as needed

# Display the chart
plt.show()

if __name__ == '__main__':
        main()

