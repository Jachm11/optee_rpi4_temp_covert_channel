from typing import List, Tuple

def compare_strings(str1: str, str2: str) -> List[int]:
    """
    Compare two strings and return the positions where they differ.
    
    Args:
        str1 (str): The first string.
        str2 (str): The second string.
        
    Returns:
        List[int]: A list of positions where the strings differ.
    """
    min_len = min(len(str1), len(str2))  # Length of the shorter string
    differences = [i for i in range(min_len) if str1[i] != str2[i]]  # List of positions with differences

    # if len(str1) != len(str2):
    #     differences.extend(range(min_len, max(len(str1), len(str2))))  # Note down the remaining positions

    if differences:
        print(f"Differences found at positions: {differences}")
    else:
        print("The strings are identical.")

    return differences

def binary_to_string(binary: str) -> str:
    """
    Convert a binary string to a human-readable string.
    
    Args:
        binary (str): The binary string to convert.
        
    Returns:
        str: The decoded string.
    """
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i + 8]  # Get the current 8-bit chunk
        result += chr(int(byte, 2))  # Convert the binary string to an integer, then to a character

    return result

def print_with_pipe(text,gap):
    for i in range(0, len(text), gap):
        print(text[i:i+gap], end='|')
    print()


def replace_non_alnum_with_asterisk(s):
    # Initialize an empty list to store the modified characters
    result = []
    # Iterate through each character in the string
    for char in s:
        # Check if the character is alphanumeric
        if char.isalnum():
            # If it is, add it to the result list
            result.append(char)
        else:
            # If it is not, add an asterisk to the result list
            result.append('*')
    # Join the list back into a string and return it
    return ''.join(result)