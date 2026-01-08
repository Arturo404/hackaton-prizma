import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded

# Example usage
image_path = "images/3.jpeg"
image_b64 = image_to_base64(image_path)

payload = {
    "image": image_b64
}


# Store result in file
import json
with open("result3.json", "w") as f:
    json.dump(payload, f, indent=2)
print("Payload stored in result.json")
