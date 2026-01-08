# Integration script: Load images, detect objects, compute displacements

import os
from PIL import Image, ImageDraw, ImageFont
import sys
import time

from video_sampler import sample_video_frames

# Import from image_processing
sys.path.append('.')
from image_processing import get_object_bounding_box, TEXT_PROMPT, processor, model

# Import from location_computing
from location_computing import compute_distance_from_camera, compute_real_length, get_bounding_box_center, compute_center_displacements

CAMERA_FOCAL_LENGTH_MM = 1612.62

def load_images_from_folder(folder_path):
    """
    Load images from a folder, sorted by filename.
    
    Args:
        folder_path (str): Path to the folder containing images
    
    Returns:
        list: List of PIL Images
    """
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
    images = []
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        try:
            img = Image.open(img_path).convert("RGB")
            images.append(img)
        except Exception as e:
            print(f"Error loading {img_file}: {e}")
    return images

def detect_objects_in_images(images, text_prompt, processor, model):
    """
    Run object detection on a list of images.
    
    Args:
        images (list): List of PIL Images
        text_prompt (str): Text prompt for detection
    
    Returns:
        list: List of detections (dicts with 'label', 'score', 'box' or None)
    """
    detections = get_object_bounding_box(images, text_prompt, processor, model)
    return detections

def compute_frame_displacements(detections, real_width, focal_length):
    """
    Compute displacements for each frame based on detections.
    
    Args:
        detections (list): List of detection dicts
        starting_location (tuple): (x, y, z) in mm
        focal_length (float): Focal length in mm
    
    Returns:
        list: List of displacements (dx, dy) in mm for each frame
    """
    if not detections or detections[0] is None:
        print("No starting detection found")
        return []
    
    # Use first detection's center as starting center
    starting_center = get_bounding_box_center(detections[0]['box'])
    
    displacements = compute_center_displacements(starting_center, detections, real_width, focal_length)
    return displacements

def get_object_center(frame):
    detection = detect_objects_in_images([frame], TEXT_PROMPT, processor, model)[0]
    if detection is None:
        return None
    bbox = detection['box']
    center = get_bounding_box_center(bbox)
    return center


def get_updated_location(frame, starting_location, object_width_mm, starting_center=None):
    start_time = time.time()
    detection = detect_objects_in_images([frame], TEXT_PROMPT, processor, model)[0]
    elapsed = time.time() - start_time
    if detection is None:
        return None
    
    bbox = detection['box']
    center = get_bounding_box_center(bbox)
    distance_mm = compute_distance_from_camera(bbox, object_width_mm, CAMERA_FOCAL_LENGTH_MM)
    if starting_center is None:
        starting_center = center
        pixel_dx, pixel_dy = 0, 0
        dx, dy = 0, 0
    else:
        pixel_dx = center[0] - starting_center[0]
        pixel_dy = center[1] - starting_center[1]
        dx = compute_real_length(pixel_dx, distance_mm, CAMERA_FOCAL_LENGTH_MM)
        dy = compute_real_length(pixel_dy, distance_mm, CAMERA_FOCAL_LENGTH_MM)

    current_position = (starting_location[0] + dx, starting_location[1] + dy, distance_mm)
    print(f"Frame:")
    print(f"  Detection time: {elapsed:.3f} seconds")
    print(f"  Center: ({center[0]:.1f}, {center[1]:.1f}) px")
    print(f"  Displacement pixel: ({pixel_dx:.2f}, {pixel_dy:.2f}) px")
    print(f"  Displacement: ({dx:.2f}, {dy:.2f}) mm")
    print(f"  Position: ({current_position[0]:.2f}, {current_position[1]:.2f}, {distance_mm:.2f}) mm")

    return current_position






# if __name__ == "__main__":
#     VIDEO_PATH = "video/drone.mp4"  # Set your video path here
#     OUTPUT_FOLDER = "output_folder"
#     ANNOTATED_FOLDER = "annotated_frames"

#     # Sample video and get greyscale frames
#     images = sample_video_frames(VIDEO_PATH, OUTPUT_FOLDER, sample_rate=1.0)
#     print(f"Sampled {len(images)} greyscale frames from {VIDEO_PATH}")

#     if not images:
#         print("No frames sampled from video.")
#         sys.exit(1)

#     starting_location = (0, 0, 330)  # Starting position in mm
#     starting_center = None
#     current_position = starting_location
#     annotated_folder = ANNOTATED_FOLDER
#     os.makedirs(annotated_folder, exist_ok=True)

#     for idx, img in enumerate(images):
#         start_time = time.time()
#         detection = detect_objects_in_images([img], TEXT_PROMPT, processor, model)[0]
#         elapsed = time.time() - start_time
#         if detection is None:
#             print(f"Frame {idx + 1}: No detection")
#             continue
#         bbox = detection['box']
#         center = get_bounding_box_center(bbox)
#         distance_mm = compute_distance_from_camera(bbox, 320, CAMERA_FOCAL_LENGTH_MM)
#         if starting_center is None:
#             starting_center = center
#             dx, dy = 0, 0
#         else:
#             pixel_dx = center[0] - starting_center[0]
#             pixel_dy = center[1] - starting_center[1]
#             dx = compute_real_length(pixel_dx, distance_mm, CAMERA_FOCAL_LENGTH_MM)
#             dy = compute_real_length(pixel_dy, distance_mm, CAMERA_FOCAL_LENGTH_MM)

#         current_position = (starting_location[0] + dx, starting_location[1] + dy, distance_mm)
#         print(f"Frame {idx + 1}:")
#         print(f"  Detection time: {elapsed:.3f} seconds")
#         print(f"  Center: ({center[0]:.1f}, {center[1]:.1f}) px")
#         print(f"  Displacement: ({dx:.2f}, {dy:.2f}) mm")
#         print(f"  Position: ({current_position[0]:.2f}, {current_position[1]:.2f}, {distance_mm:.2f}) mm")
#         # Annotate image
#         draw = ImageDraw.Draw(img)
#         font = ImageFont.load_default()
#         x1, y1, x2, y2 = bbox
#         draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
#         draw.ellipse([center[0]-5, center[1]-5, center[0]+5, center[1]+5], fill="blue")
#         text_lines = [
#             f"Center: ({center[0]:.1f}, {center[1]:.1f}) px",
#             f"Position: ({current_position[0]:.2f}, {current_position[1]:.2f}, {distance_mm:.2f}) mm"
#         ]
#         y_offset = y1 - 40
#         for line in text_lines:
#             draw.text((x1, y_offset), line, fill="white", font=font)
#             y_offset += 15
#         annotated_path = os.path.join(annotated_folder, f"annotated_frame_{idx+1:04d}.jpg")
#         img.save(annotated_path)
#         print(f"  Saved annotated image: {annotated_path}")
#         try:
#             img.show()
#         except Exception:
#             pass
