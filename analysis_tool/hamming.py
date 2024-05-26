import math
from typing import Optional

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
    hamming.multiple_errors = (parity % 2 == int(data[0])) and (hamming.error != 0)
    
    return hamming

def correct_error(decode: HammingDecode) -> str:
    """Correct errors in a decoded Hamming message."""
    decode_message = decode.message
    error_index = decode.error

    # If no error, return the original message
    if error_index == 0:
        return decode_message

    # Correct the error at the error_index
    corrected_message = (
        decode_message[:error_index] +
        ('0' if decode_message[error_index] == '1' else '1') +
        decode_message[error_index + 1:]
    )

    return corrected_message

# block0 = "0010101110001110"
# res = extended_hamming(block0)
# print("Message:         ",res.message)
# print("Error in pos:    ",res.error)
# print("Multiple errors: ",res.multiple_errors)
# print("Correction:      ",correct_error(res))