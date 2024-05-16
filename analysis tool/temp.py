import matplotlib.pyplot as plt

# Read temperatures from file
with open("temp_log", "r") as file:
    temperatures = [int(line.strip()) for line in file]

# Create x-axis values (assuming one data point per unit)
x_values = range(1, len(temperatures) + 1)

# Create the graph
plt.plot(x_values, temperatures, marker='o', linestyle='-')

# Add vertical red lines every 50 data points
for i in range(50, len(temperatures) + 1, 50):
    plt.axvline(x=i, color='r', linestyle='--')

# Label the graph
plt.title('Temperature over Time')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')

# Display the graph
plt.grid(True)
plt.show()
