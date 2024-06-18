import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('results/metrics/metrics_low_freq_3000.csv')

# Convert columns to appropriate data types if necessary
df['Accuracy'] = df['Accuracy'].astype(float)
df['Throughput'] = df['Throughput'].astype(float)
df['Transfer Time'] = df['Transfer Time'].astype(float)

# Filter the rows where Hamming is True
hamming_true = df[df['Hamming'] == True]

# Filter the rows where Hamming is False
hamming_false = df[df['Hamming'] == False]

# Calculate average values for Hamming True
avg_accuracy_true = hamming_true['Accuracy'].mean()
avg_throughput_true = hamming_true['Throughput'].mean()
avg_transfer_time_true = hamming_true['Transfer Time'].mean()

# Calculate average values for Hamming False
avg_accuracy_false = hamming_false['Accuracy'].mean()
avg_throughput_false = hamming_false['Throughput'].mean()
avg_transfer_time_false = hamming_false['Transfer Time'].mean()

# Print the results
print(f'For rows where Hamming is True:')
print(f'Average Accuracy: {avg_accuracy_true}')
print(f'Average Throughput: {avg_throughput_true}')
print(f'Average Transfer Time: {avg_transfer_time_true}\n')

print(f'For rows where Hamming is False:')
print(f'Average Accuracy: {avg_accuracy_false}')
print(f'Average Throughput: {avg_throughput_false}')
print(f'Average Transfer Time: {avg_transfer_time_false}')
