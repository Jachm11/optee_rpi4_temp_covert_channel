import os
import subprocess
import math
import time
import csv
import matplotlib.pyplot as plt
from typing import List, Tuple
from hamming import *
from utils import *
import easygui

global iter
global total

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

        # print(f"Temps from {i} to {i + temps_per_bit}")

        if prev_avg is None:
            value = '0'
        elif (prev_avg+tolerance) >= avg_temp >= (prev_avg-tolerance) :
            value = prev_value
        elif avg_temp > prev_avg:
            value = '1'
        else:
            value = '0'

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

    # Set y-axis ticks
    plt.yticks([i/10 for i in range(int(min(temperatures)*10), int(max(temperatures)*10)+1)])

    # Add the text below the graph
    plt.text(0.5, -0.1, text, ha='center', fontsize=12, transform=plt.gca().transAxes)

    # Display the graph
    plt.grid(True)
    plt.show()

def run_rpi4(milis:int, hamming:bool, sampling:int, msg_size:int) -> str:
    """
    Runs a the command that runs the channel on the Raspberry Pi 4 and returns the output.

    Parameters:
    milis (int): The duration in milliseconds for the measurement.
    hamming (bool): Whether to use Hamming encoding.
    sampling (int): The sampling rate in milliseconds.
    msg_size (int): The size of the message in bytes.

    Returns:
    str: The output of the command.
    """
    # Define the shell command
    measurements = int((milis/(sampling/1000)) * msg_size)
    command = "./analysis_tool/shell_scripts/run_on_pi " + str(milis) + " " + str(int(hamming)) + " " + str(measurements) + " " + str(sampling)
    print(command)

    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    return result.stdout

def analyze_single_test(interval: int, hamming: bool, hamming_block_size: int, sample_rate:int, path:str ,image:bool = False, plot:bool = True) -> List:
    """
    Analyzes a single test run for decoding a temperature-based binary message.

    Args:
    interval (int): The interval in milliseconds between temperature samples.
    hamming (bool): Whether to use Hamming code for error correction.
    hamming_block_size (int): The block size for Hamming code.
    sample_rate (int): The sample rate in Hz for temperature measurements.
    path (str): The file path to the temperature data file.
    image (bool, optional): Whether to decode the message as an image. Defaults to False.
    plot (bool, optional): Whether to plot the temperature data over time. Defaults to True.

    Returns:
    List: A list containing metrics of the decoding process including accuracy, bit rate, total errors, error rate, corrected errors, correction rate, meaningful errors, throughput, total transfer time, raw message, decoded message, and readable message.
    """
    hamming_truth = "011001101100001111100111110110111000000101000010"
    truth = "01101000011011110110110001100001"
    msg = ''
    plot_truth = hamming_truth

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

    # Read temperatures from file
    with open(path, "r") as file:
        temperatures = [float(line.strip()) for line in file]

    # Decode temps
    temps_per_bit = interval // sample_rate
    raw_msg = decode_temp_msg(temperatures, temps_per_bit,interval/10000)

    if (image):
        stringed = ''.join(map(str,raw_msg))
        output_path = 'dino_100.png'  # Specify the output path
        image = binary_string_to_image(stringed,32,32,output_path)
        image.show()  # This will display the image
        return     

    # Calculate bit rate
    total_transfer_time = (len(raw_msg)*(interval / 1000))
    bit_rate = len(raw_msg)/total_transfer_time

    print("---------MESSAGES---------")
    if hamming:
        print("---Hamming---")
        # Decoding
        msg, _, _, corrected_errors = extract_hamming_message(raw_msg, hamming_block_size)

        # Calculate metrics
        total_errors = len(compare_strings(raw_msg,hamming_truth))
        correction_rate = corrected_errors / len(raw_msg)

        print("Hamming Truth:")
        print_with_pipe(hamming_truth,16)
        print("Raw message:")
        print_with_pipe(raw_msg,16)
        differences = compare_strings(raw_msg, hamming_truth)
        if differences:
            print(f"Differences found at positions: {differences}")
        else:
            print("The strings are identical.")

    else:
        # No need to decode, directly compare
        msg = raw_msg
        plot_truth = truth

        # Calculate metrics
        total_errors = len(compare_strings(msg,truth))

    print("---Decode---")
    error_rate = total_errors / len(raw_msg)
    meaningful_errors = len(compare_strings(msg[:len(truth)], truth))

    #Print message
    print("Truth:")
    print_with_pipe(truth,8)
    print("Extracted message:")
    print_with_pipe(msg,8)
    differences = compare_strings(msg, truth)
    if differences:
        print(f"Differences found at positions: {differences}")
    else:
        print("The strings are identical.")

    readable = binary_to_string(msg)
    readable = replace_non_alnum_with_asterisk(readable)
    print("Final message:")
    print(readable)

    # Throughput
    throughput = (len(msg) - meaningful_errors)/total_transfer_time
    accuracy = (len(msg[:len(truth)]) - meaningful_errors)/len(truth) * 100

    # Print stats
    print("---------METRICS---------")
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
    
    if (plot):
        plot_temperature_over_time(temperatures,temps_per_bit,plot_truth + '\n' + msg)

    return accuracy, bit_rate, total_errors, error_rate, corrected_errors, correction_rate, meaningful_errors, throughput, total_transfer_time, raw_msg, msg, readable

def run_single_test(interval: int, hamming: bool, hamming_block_size: int, sample_rate:int, image:bool = False, plot:bool = True) -> None:
    """
    Runs a single test for collecting and analyzing temperature-based binary messages from the RPI4.

    Args:
    interval (int): The interval in milliseconds between temperature samples.
    hamming (bool): Whether to use Hamming code for error correction.
    hamming_block_size (int): The block size for Hamming code.
    sample_rate (int): The sample rate in Hz for temperature measurements.
    image (bool, optional): Whether to decode the message as an image. Defaults to False.
    plot (bool, optional): Whether to plot the temperature data over time. Defaults to True.

    Returns:
    None
    """
    hamming_truth = "011001101100001111100111110110111000000101000010"
    truth = "01101000011011110110110001100001"
    global iter

    if image:
        raw_temps = run_rpi4(interval, hamming, sample_rate*1000, 1024)
    elif hamming:
        raw_temps = run_rpi4(interval, hamming, sample_rate*1000, len(hamming_truth))
    else:
        raw_temps = run_rpi4(interval, hamming, sample_rate*1000, len(truth))

    # Save temporally
    temp_path = f'results/runs/.temp.txt'
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, 'w') as temp_file:
        temp_file.write(raw_temps)

    accuracy, bit_rate, total_errors, error_rate, corrected_errors, correction_rate, meaningful_errors, throughput, total_transfer_time, raw_msg, msg, readable = analyze_single_test(interval,hamming,hamming_block_size,sample_rate,temp_path,image,plot)

    # Save for later use
    directory = f'results/runs/{interval}'
    filename = f'{iter}_{hamming}_{int(accuracy)}.txt'
    file_path = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(raw_temps)
    
    # Delete the temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Save metrics to CSV
    csv_file = f'results/metrics/metrics_{interval}.csv'
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_MINIMAL,  escapechar='\\')
        if not file_exists:
            # Write header if the file doesn't exist
            writer.writerow(['Interval','Hamming','Sample rate','Bit Rate', 'Total Errors', 'Error Rate', 'Corrected Errors', 'Correction Rate', 'Meaningful Errors', 'Throughput', 'Transfer Time', 'Accuracy','Raw message','Message','String'])
        # Write the metrics
        writer.writerow([interval,hamming,sample_rate,bit_rate, total_errors, error_rate, corrected_errors if hamming else 'N/A', correction_rate if hamming else 'N/A', meaningful_errors, throughput, total_transfer_time, accuracy, raw_msg, msg, str(readable)])

    return

def main():
    global iter
    iter = "single"

    def get_user_input(prompt, default):
        user_input = input(f"{prompt} [{default}]: ").strip().lower()
        return user_input if user_input else default.lower()

    def parse_boolean_input(user_input):
        return user_input in ['yes', 'y']

    def analyze_previous_test():
        interval = int(get_user_input("Enter interval (ms)", "3000"))
        hamming = parse_boolean_input(get_user_input("Use Hamming code? (yes/no)", "no"))
        hamming_block_size = int(get_user_input("Enter Hamming block size", "16"))
        sample_rate = int(get_user_input("Enter sample rate (ms)", "10"))

        # Open file dialog for the user to select a file
        path = easygui.fileopenbox(title="Select the test file", filetypes=[["*.txt", "Text Files"]])
        if not path:
            print("No file selected. Exiting.")
            return

        image = parse_boolean_input(get_user_input("Analyze as image? (yes/no)", "no"))
        plot = parse_boolean_input(get_user_input("Plot data? (yes/no)", "yes"))

        analyze_single_test(interval, hamming, hamming_block_size, sample_rate, path, image, plot)

    def run_new_test():
        interval = int(get_user_input("Enter interval (ms)", "3000"))
        hamming = parse_boolean_input(get_user_input("Use Hamming code? (yes/no)", "no"))
        hamming_block_size = int(get_user_input("Enter Hamming block size", "16"))
        sample_rate = int(get_user_input("Enter sample rate (ms)", "10"))
        image = parse_boolean_input(get_user_input("Analyze as image? (yes/no)", "no"))
        plot = parse_boolean_input(get_user_input("Plot data? (yes/no)", "yes"))

        run_single_test(interval, hamming, hamming_block_size, sample_rate, image, plot)

    def full_analysis_sweep():
        print("Full analysis sweep will take a long time. Do you want to proceed? (yes/no)")
        confirmation = input().strip().lower()
        if confirmation in ['yes', 'y']:
            start_time = time.time()

            for i in range(0, 20):
                iter = i
                hamming = False
                interval = 5000
                sample_rate = 10  # Wait 10ms --> 100Hz sampling

                while interval >= 10:
                    run_single_test(interval, hamming, 16, sample_rate, plot=False)
                    if interval == 1000:
                        interval -= 500
                    elif interval <= 500:
                        interval -= 100
                    else:
                        interval -= 1000

                interval = 5000
                hamming = False

                while interval >= 10:
                    run_single_test(interval, hamming, 16, sample_rate, plot=False)
                    if interval == 1000:
                        interval -= 500
                    elif interval <= 500:
                        interval -= 100
                    else:
                        interval -= 1000

            end_time = time.time()
            elapsed_time = (end_time - start_time)
            elapsed_time_hours = elapsed_time / 60 / 60

            print(f"Execution Time: {elapsed_time:.6f} seconds")
            print(f"Execution Time: {elapsed_time_hours:.6f} hours")

    while True:
        print("Select an option:")
        print("1. Analyze a previous test")
        print("2. Run a new test")
        print("3. Perform a full analysis sweep")
        print("4. Exit")
        choice = input().strip()

        if choice == '1':
            analyze_previous_test()
        elif choice == '2':
            run_new_test()
        elif choice == '3':
            full_analysis_sweep()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()