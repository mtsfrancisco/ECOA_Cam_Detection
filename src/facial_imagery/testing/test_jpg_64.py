import os
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from image_conversions import image_to_base64

def main():
    # Hide the root window
    Tk().withdraw()

    # Prompt the user to select an image file
    image_path = askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )

    if not image_path:
        print("No file selected.")
        return

    # Convert the selected image to a Base64 string and get the JSON object
    json_data = image_to_base64(image_path)

    # Define the path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), 'example_base64.json')

    # Read the existing content of the JSON file
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append the new data to the existing content
    existing_data.append(json.loads(json_data))

    # Write the updated content back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

    print("Data appended to example_base64.json")

if __name__ == "__main__":
    main()