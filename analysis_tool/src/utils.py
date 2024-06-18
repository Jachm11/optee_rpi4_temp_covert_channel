from typing import List
from PIL import Image

def is_power_2(x: int) -> bool:
    """
    Check if a number is a power of 2.

    Parameters:
    x (int): The number to check.

    Returns:
    bool: True if x is a power of 2, False otherwise.
    """
    return x and not (x & (x - 1))

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

    # Leaving commented to ignore extra elements
    # if len(str1) != len(str2):
    #     differences.extend(range(min_len, max(len(str1), len(str2))))  # Note down the remaining positions

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

def print_with_pipe(text:str, gap:int) -> None :
    """
    Prints the given text with a pipe '|' character inserted after every 'gap' characters.

    Parameters:
        text (str): The text to be printed.
        gap (int): The number of characters after which to insert the pipe character.

    Returns:
        None

    Example:
        >>> print_with_pipe("Hello World", 2)
        He|ll|o |Wo|rld|
    """
    for i in range(0, len(text), gap):
        # Print a slice of 'text' starting from index 'i' and ending at 'i + gap'.
        # The 'end' parameter ensures that each print statement ends with '|', instead of a newline.
        print(text[i:i+gap], end='|')
    # Print a newline to end the line after all characters have been printed.
    print()

def replace_non_alnum_with_asterisk(string:str) -> str:
    """
    Replaces non-alphanumeric characters in a string with asterisks ('*').

    Parameters:
        string (str): The input string to process.

    Returns:
        str: A new string where non-alphanumeric characters are replaced with asterisks.

    Example:
        >>> replace_non_alnum_with_asterisk("Hello, world! How are you?")
        'Hello**world*How*are*you'
    """
    result = []
    for char in string:
        # Check if the character is alphanumeric
        if char.isalnum():
            result.append(char)
        else:
            result.append('*')
    return ''.join(result)

def binary_string_to_image(binary_string: str, width: int, height: int, output_path: str) -> Image.Image:
    """
    Converts a binary string to a 1-bit pixel image and saves it to the specified path.
    
    Parameters:
    binary_string (str): The input binary string representing pixel data.
    width (int): The width of the image.
    height (int): The height of the image.
    output_path (str): The path where the generated image will be saved.
    
    Returns:
    Image.Image: The generated image object.
    
    Raises:
    ValueError: If the length of the binary string exceeds the specified dimensions.
    """
    # Calculate the required length
    required_length = width * height
    
    # Pad the binary string with '1's if its length does not match the required length
    if len(binary_string) < required_length:
        binary_string += '1' * (required_length - len(binary_string))
    elif len(binary_string) > required_length:
        raise ValueError("The length of the binary string exceeds the specified dimensions.")
    
    # Create a new image with the given width and height, mode '1' for 1-bit pixels
    img = Image.new('1', (width, height))
    
    # Populate the image with pixels based on the binary string
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            # Calculate the position in the binary string
            index = y * width + x
            # Set the pixel value (255 for white, 0 for black)
            pixels[x, y] = 255 if binary_string[index] == '1' else 0
    
    # Save the image
    img.save(output_path)
    print(f"Image saved as {output_path}")
    return img

def isfloat(num: str) -> bool:
    """
    Checks if a string can be converted to a float.

    Parameters:
    num (str): The input string to check.

    Returns:
    bool: True if the input string can be converted to a float, False otherwise.
    """
    try:
        float(num) 
        return True 
    except ValueError:
        return False
    
def merge_binary_strings(strings: list) -> str:
    """
    Merges multiple binary strings into one, considering majority voting at each position.

    Parameters:
    strings (list): A list of binary strings to be merged.

    Returns:
    str: The merged binary string.
    """
    # Assuming all strings are of the same length
    length = len(strings[0])
    
    result = []
    for i in range(length):
        # Count the number of '1's at position i across all strings
        count = sum(string[i] == '1' for string in strings)
        # Determine the majority value
        if count > len(strings) // 2:
            result.append('1')
        else:
            result.append('0')
    
    return ''.join(result)