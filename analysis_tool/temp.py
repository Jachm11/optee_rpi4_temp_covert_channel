import matplotlib.pyplot as plt
from typing import List, Tuple
import subprocess
import math
import os
import csv
from hamming import *
from utils import *

def decode_temp_msg(temps: List[float], temps_per_bit: int, tolerance:float) -> str:
    """
    Decode a message from temperature readings.
    
    Args:
        temps (List[float]): A list of temperature readings.
        temps_per_bit (int): Number of temperature readings per bit.
        
    Returns:
        str: The decoded binary message.
    """
    result = ''
    prev_avg: Optional[float] = None  # Store the average temperature of the previous group
    prev_value = ''

    for i in range(0, len(temps), temps_per_bit):
        group = temps[i:i + temps_per_bit]  # Get the current group of temperatures
        avg_temp = sum(group) / len(group)  # Calculate the average temperature of the current group
        value = ''

        if prev_avg is None:
            value = '0'
        elif (prev_avg+tolerance) >= avg_temp >= (prev_avg-tolerance) :
            value = prev_value
        elif avg_temp > prev_avg:
            value = '1'
        else:
            value = '0'

        #print(i/temps_per_bit,prev_avg,avg_temp)
        result += value


        prev_avg = avg_temp  # Update the previous average temperature
        prev_value = value

    return result

def extract_hamming_message(msg: str, block_size: int) -> Tuple[str, List[str], List[int], int]:
    """
    Extract and decode a message from a binary string divided into blocks.
    
    Args:
        num_blocks (int): Number of blocks in the message.
        msg (str): The binary string containing the encoded message.
        
    Returns:
        Tuple[str, List[str], List[int]]: The full decoded message, blocks with errors, and indices of faulty blocks.
    """

    num_blocks = math.ceil(len(msg)/block_size)
    blocks = [msg[i * block_size: (i + 1) * block_size] for i in range(num_blocks)]

    decoded_messages = []
    blocks_with_errors = []
    faulty_block_indices = []
    corrected_msg = ""
    corrected_errors = 0

    for index, block in enumerate(blocks):
        hamming_decode = extended_hamming(block)
        if not hamming_decode.multiple_errors:
            corrected_msg, error = correct_error(hamming_decode)
            corrected_errors += error
            decoded_messages.append(corrected_msg)
        else:
            blocks_with_errors.append(block)
            faulty_block_indices.append(index)
            decoded_messages.append(hamming_decode.message)

    full_message = ''.join(decoded_messages)
    return full_message, blocks_with_errors, faulty_block_indices, corrected_errors

def plot_temperature_over_time(temperatures: List[float], interval: int, text: str) -> None:
    """
    Plot temperature data over time with vertical lines at specified intervals
    and display a text below the graph.
    
    Args:
        temperatures (List[float]): A list of temperature readings.
        interval (int): The interval at which to add vertical lines.
        text (str): The text to be displayed below the graph.
    """
    
    x_values = range(1, len(temperatures) + 1)  # Create x-axis values
    plt.plot(x_values, temperatures, marker='o', linestyle='-')

    # Add vertical red lines at specified intervals
    for i in range(interval, len(temperatures) + 1, interval):
        plt.axvline(x=i, color='r', linestyle='--')

    plt.title('Temperature over Time')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')

    # Add the text below the graph
    plt.text(0.5, -0.1, text, ha='center', fontsize=12, transform=plt.gca().transAxes)

    # Display the graph
    plt.grid(True)
    plt.show()

def run_rpi4(milis:int, hamming:bool) -> str:

    # Define the command you want to run
    command = "./analysis_tool/run_on_pi " + str(milis) + " " + str(int(hamming))
    print(command)

    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    return result.stdout


def run_single_test(interval: int, hamming: bool, hamming_block_size: int):
    hamming_truth = "011001101100001111100111110110111000000101000010"
    truth = "01101000011011110110110001100001"
    msg = ''

    # Metrics
    bit_rate = 0
    total_errors = 0
    error_rate = 0
    corrected_errors = 0
    correction_rate = 0
    meaningful_errors = 0
    throughput = 0
    total_transfer_time = 0
    accuracy = 0

    # Execution
    raw_temps = run_rpi4(interval, hamming)

    # Parse and convert temperatures to integers
    temperatures = [int(temp) for temp in raw_temps.split('\n') if temp.isdigit()]

    # # Read temperatures from file
    # with open("temp_log", "r") as file:
    #     temperatures = [int(line.strip()) for line in file]

    # Decode temps
    temps_per_bit = interval // 100
    raw_msg = decode_temp_msg(temperatures, temps_per_bit,interval/10000)

    # print("Hamming truth: ",hamming_truth)
    # print("Raw message:   ",raw_msg)

    print_with_pipe(hamming_truth,16)
    print_with_pipe(raw_msg,16)
    

    # Calculate bit rate
    total_transfer_time = (len(raw_msg)*(interval / 1000))
    bit_rate = len(raw_msg)/total_transfer_time

    if hamming:
        # Decoding
        msg, _, error_indices, corrected_errors = extract_hamming_message(raw_msg, hamming_block_size)

        # Calculate total errors and corrected errors
        total_errors = len(compare_strings(raw_msg,hamming_truth))

        # Error rate and correction rate
        error_rate = total_errors / len(raw_msg)
        correction_rate = corrected_errors / len(raw_msg)

        # Calculate meaningful errors
        meaningful_errors = len(compare_strings(msg[:len(truth)], truth))
    else:
        # No need to decode, directly compare
        msg = raw_msg

        # Calculate meaningful errors
        meaningful_errors = len(compare_strings(msg, truth))
        total_errors = meaningful_errors

        # Error rate
        error_rate = total_errors / len(raw_msg)

    # print("Truth:   ",truth)
    # print("Message: ",msg)

    print_with_pipe(truth,8)
    print_with_pipe(msg,8)

    # Throughput
    throughput = (len(msg) - meaningful_errors)/total_transfer_time
    accuracy = (len(msg[:len(truth)]) - meaningful_errors)/len(truth) * 100

    # Print stats
    print(f"Bit Rate: {bit_rate:.4f} bit/s")
    print(f"Total Errors: {total_errors}")
    print(f"Error Rate: {error_rate:.4f}")
    if hamming:
        print(f"Corrected Errors: {corrected_errors}")
        print(f"Correction Rate: {correction_rate:.4f}")
    print(f"Meaningful Errors: {meaningful_errors}")
    print(f"Throughput: {throughput:.4f} bit/s")
    print(f"Transfer time: {total_transfer_time:.4f} s")
    print(f"Accuracy: {accuracy:.4f}%")
    
    readable = binary_to_string(msg)

    print(readable)

    # Save metrics to CSV
    csv_file = 'metrics.csv'
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_MINIMAL,  escapechar='\\')
        if not file_exists:
            # Write header if the file doesn't exist
            writer.writerow(['Interval','Hamming','Sample rate','Bit Rate', 'Total Errors', 'Error Rate', 'Corrected Errors', 'Correction Rate', 'Meaningful Errors', 'Throughput', 'Transfer Time', 'Accuracy','Raw message','Message','String'])
        # Write the metrics
        writer.writerow([interval,hamming,100,bit_rate, total_errors, error_rate, corrected_errors if hamming else 'N/A', correction_rate if hamming else 'N/A', meaningful_errors, throughput, total_transfer_time, accuracy, raw_msg, msg, str(readable)])

    #plot_temperature_over_time(temperatures,temps_per_bit,"sas")

    return 



def main():

    # Config
    hamming = True
    interval = 5000

    while interval >= 100:
        run_single_test(interval, hamming, 16)
        interval -= 200

    interval = 5000
    hamming = False

    while interval >= 100:
        run_single_test(interval, hamming, 16)
        interval -= 200

if __name__ == '__main__':
    main()
