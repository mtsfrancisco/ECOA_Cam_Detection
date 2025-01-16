import base64
import os
import json
from PIL import Image
from io import BytesIO

def image_to_base64(image_path):
    """
    Convert an image file to a Base64 string and return a JSON object.
    
    Args:
        image_path (str): Path to the image file.
    
    Returns:
        str: JSON object containing the image name and Base64-encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode("utf-8")

    image_name = os.path.basename(image_path)
    image_extension = image_path.split('.')[-1]
    base64_data = f"data:image/{image_extension};base64,{base64_string}"

    # Create a JSON object
    json_data = json.dumps({
        "image_name": image_name,
        "base64_string": base64_data
    })

    return json_data

def base64_to_image(base64_string, output_filename):
    """
    Convert a Base64 string back to an image file and save it to the faces folder.
    
    Args:
        base64_string (str): Base64-encoded string of the image.
        output_filename (str): Filename to save the decoded image file.
    """
    # Remove the Base64 prefix if it exists (e.g., data:image/png;base64,)
    if base64_string.startswith("data:image"):
        base64_string = base64_string.split(",")[1]
    
    image_data = base64.b64decode(base64_string)
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the output path in the faces folder
    faces_folder = os.path.join(current_dir, "faces")
    os.makedirs(faces_folder, exist_ok=True)
    output_path = os.path.join(faces_folder, output_filename)
    
    with open(output_path, "wb") as output_file:
        output_file.write(image_data)