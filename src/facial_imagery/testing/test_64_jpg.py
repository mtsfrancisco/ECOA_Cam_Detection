import os
import json
from image_conversions import base64_to_image

def main():
    # Define the path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), 'example_base64.json')

    # Read the content of the JSON file
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print("Error: JSON file is empty or invalid.")
                return
    else:
        print("Error: JSON file does not exist.")
        return

    # Define the path to the example folder
    example_folder = os.path.join(os.path.dirname(__file__), 'example_result')
    os.makedirs(example_folder, exist_ok=True)

    # Decode each Base64 string and save the images to the example folder
    for item in data:
        image_name = item['image_name']
        base64_string = item['base64_string']
        output_path = os.path.join(example_folder, image_name)
        base64_to_image(base64_string, output_path)

    print("Images have been saved to the example folder.")

if __name__ == "__main__":
    main()