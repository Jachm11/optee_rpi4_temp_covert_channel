import math
from typing import Optional, Tuple


class HammingDecode:
    def __init__(self) -> None:
        self.message: Optional[str] = None
        self.error: int = 0
        self.multiple_errors: bool = False

def is_power_2(x: int) -> bool:
    """Check if a number is a power of 2."""
    return x and not (x & (x - 1))

def extended_hamming(data: str) -> HammingDecode:
    """Decode an extended Hamming code."""
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
    """Correct errors in a decoded Hamming message."""
    decode_message = decode.message
    error_index = map_index(decode.error)

    # No errors
    if error_index == -2:
        return (decode_message,0)

    # Error on partity bit no data comprimises
    if error_index == -1:
        return (decode_message,1)

    # Correct the error at the error_index
    try:
        corrected_message = (
            decode_message[:error_index] +
            ('0' if decode_message[error_index] == '1' else '1') +
            decode_message[error_index + 1:]
        )
    except:
        return (decode_message,1)

    return (corrected_message,1)

def map_index(index:int)->int:

    match index:
        case 0:
            return -2
        case 1:
            return -1
        case 2:
            return -1
        case 3:
            return 0
        case 4:
            return -1
        case 5:
            return 1
        case 6:
            return 2
        case 7:
            return 3
        case 8:
            return -1
        case 9:
            return 4
        case 10:
            return 5
        case 11:
            return 6
        case 12:
            return 7
        case 13:
            return 8
        case 14:
            return 9
        case 15:
            return 10

# block0 = "1110100011011011"
# res = extended_hamming(block0)
# print("Message:         ",res.message)
# print("Error in pos:    ",res.error)
# print("Multiple errors: ",res.multiple_errors)
# print("Correction:      ",correct_error(res))