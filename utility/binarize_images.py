from PIL import Image

def image_to_binary_string(image_path):
    # Open the image
    with Image.open(image_path) as img:
        # Resize the image to 32x32 pixels
        img = img.resize((32, 32))
        # Ensure the image is in binary (1-bit pixels, black and white)
        bw_image = img.convert('1')
        
        # Get the size of the image
        width, height = bw_image.size
        
        # Initialize an empty string to store the binary representation
        binary_string = ""
        
        # Traverse the image pixels
        for y in range(height):
            for x in range(width):
                # Get the pixel value (0 for black, 255 for white)
                pixel = bw_image.getpixel((x, y))
                # Append '0' for black pixels and '1' for white pixels
                binary_string += '1' if pixel == 255 else '0'
    
    return binary_string

def binary_string_to_image(binary_string, width, height, output_path):
    # Ensure the length of the binary string matches the provided dimensions
    if len(binary_string) != width * height:
        raise ValueError("The length of the binary string does not match the specified dimensions.")
    
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

# Example usage
image_path = 'dino3232.png'
binary_string = image_to_binary_string(image_path)
print((binary_string))

output_path = 'output_image.png'  # Specify the output path
image = binary_string_to_image(binary_string, 32, 32, output_path)
image.show()  # This will display the image

