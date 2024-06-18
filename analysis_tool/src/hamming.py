import math
from utils import is_power_2
from typing import Optional, Tuple

class HammingDecode:
    def __init__(self) -> None:
        """
        Initialize the HammingDecode object.

        Attributes:
        message (Optional[str]): The decoded message, initialized as None.
        error (int): The position of the detected error, initialized to 0.
        multiple_errors (bool): A flag indicating if multiple errors were detected, initialized to False.
        """
        self.message: Optional[str] = None
        self.error: int = 0
        self.multiple_errors: bool = False

def map_index(index: int) -> int:
    """
    Map an index from the extended Hamming code error detection to the corresponding data bit index.

    Parameters:
    index (int): The index from the Hamming code error detection.

    Returns:
    int: The mapped index, where -2 indicates no error, -1 indicates a parity bit error, 
         and non-negative values indicate data bit indices.
    """
    match index:
        case 0:
            return -2  # No errors detected
        case 1:
            return -1  # Error in parity bit
        case 2:
            return -1  # Error in parity bit
        case 3:
            return 0   # Error in data bit at index 0
        case 4:
            return -1  # Error in parity bit
        case 5:
            return 1   # Error in data bit at index 1
        case 6:
            return 2   # Error in data bit at index 2
        case 7:
            return 3   # Error in data bit at index 3
        case 8:
            return -1  # Error in parity bit
        case 9:
            return 4   # Error in data bit at index 4
        case 10:
            return 5   # Error in data bit at index 5
        case 11:
            return 6   # Error in data bit at index 6
        case 12:
            return 7   # Error in data bit at index 7
        case 13:
            return 8   # Error in data bit at index 8
        case 14:
            return 9   # Error in data bit at index 9
        case 15:
            return 10  # Error in data bit at index 10

def extended_hamming(data: str) -> HammingDecode:
    """
    Decode an extended Hamming code.

    Parameters:
    data (str): The encoded data string representing the Hamming code.

    Returns:
    HammingDecode: An object containing the decoded message and error information.
    """
    size = len(data)
    hamming = HammingDecode()
    parity = 0
    data_index = 0
    data_bits = size - int(math.log2(size)) + 1

    # Initialize message as a list of the appropriate size
    message = [''] * data_bits

    for i in range(size):
        if data[i] == '1':
            hamming.error ^= i
            parity += 1

        if not is_power_2(i) and i != 0:
            message[data_index] = data[i]
            data_index += 1

    # Convert list to string
    hamming.message = ''.join(message)
    hamming.multiple_errors = not(parity % 2 == int(data[0])) and (hamming.error != 0)
    
    return hamming

def correct_error(decode: HammingDecode) -> Tuple[str, int]:
    """
    Correct errors in a decoded Hamming message.

    Parameters:
    decode (HammingDecode): The decoded Hamming message with error information.

    Returns:
    Tuple[str, int]: A tuple containing the corrected message and an error indicator.
                     The error indicator is 0 if no errors were found, 1 if an error was corrected.
    """
    decode_message = decode.message
    error_index = map_index(decode.error)

    # No errors detected in the message
    if error_index == -2:
        return (decode_message, 0)

    # Error detected on a parity bit; no data bits are compromised
    if error_index == -1:
        return (decode_message, 1)

    # Correct the error at the identified error_index
    try:
        corrected_message = (
            decode_message[:error_index] +
            ('0' if decode_message[error_index] == '1' else '1') +
            decode_message[error_index + 1:]
        )
    except:  # Catch any errors that occur during correction
        return (decode_message, 1)

    # Return the corrected message with an error indicator
    return (corrected_message, 1)

# Example usage. Uncomment to try

# block0 = "1110100011011111"
# res = extended_hamming(block0)
# print("Message:         ",res.message)
# print("Error in index:  ",res.error)
# print("Multiple errors: ",res.multiple_errors)
# print("Correction:      ",correct_error(res))