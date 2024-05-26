import matplotlib.pyplot as plt
from typing import List, Tuple
import subprocess
from hamming import *
from utils import *

def decode_temp_msg(temps: List[float], temps_per_bit: int) -> str:
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

    for i in range(0, len(temps), temps_per_bit):
        group = temps[i:i + temps_per_bit]  # Get the current group of temperatures
        avg_temp = sum(group) / len(group)  # Calculate the average temperature of the current group

        if prev_avg is not None and avg_temp >= prev_avg:
            result += '1'
        else:
            result += '0'

        prev_avg = avg_temp  # Update the previous average temperature

    return result

def extract_hamming_message(num_blocks: int, msg: str) -> Tuple[str, List[str], List[int]]:
    """
    Extract and decode a message from a binary string divided into blocks.
    
    Args:
        num_blocks (int): Number of blocks in the message.
        msg (str): The binary string containing the encoded message.
        
    Returns:
        Tuple[str, List[str], List[int]]: The full decoded message, blocks with errors, and indices of faulty blocks.
    """
    block_size = len(msg) // num_blocks
    blocks = [msg[i * block_size: (i + 1) * block_size] for i in range(num_blocks)]

    decoded_messages = []
    blocks_with_errors = []
    faulty_block_indices = []

    for index, block in enumerate(blocks):
        hamming_decode = extended_hamming(block)
        if not hamming_decode.multiple_errors:
            corrected_msg = correct_error(hamming_decode)
            decoded_messages.append(corrected_msg)
        else:
            blocks_with_errors.append(block)
            faulty_block_indices.append(index)

    full_message = ''.join(decoded_messages)
    return full_message, blocks_with_errors, faulty_block_indices

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


def main():

    # Read temperatures from file
    with open("temp_log", "r") as file:
        temperatures = [int(line.strip()) for line in file]

    hamming = True
    is_string = True

    temps_per_bit = 50
    msg = decode_temp_msg(temperatures, temps_per_bit)
    print(msg)

    org = "011001101100001111100111110110111000000101000010"
    print(org)
    compare_strings(msg,org)

    if (hamming):

        num_blocks = 3
        msg, errors, error_indices = extract_hamming_message(num_blocks, msg)

    print(msg)
    print("01101000011011110110110001100001")

    if (is_string):

        msg = binary_to_string(msg)

    print(msg)

    #plot_temperature_over_time(temperatures,50,decode_temp_msg(temperatures, temps_per_bit))


    # Define the command you want to run
    command = "./analysis_tool/run_on_pi"

    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Print the output
    print("Command output:")
    print(result.stdout)



if __name__ == '__main__':
    main()
