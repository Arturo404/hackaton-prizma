# Configuration for phone and camera
PHONE_REAL_WIDTH_MM = 159.8  # Real width of the phone in millimeters (adjust as needed)
CAMERA_FOCAL_LENGTH_MM = 1386  # Focal length of the camera in millimeters (adjust as needed)

def get_bounding_box_width_pixels(bbox):
    """
    Compute the width of the bounding box in pixels.
    
    Args:
        bbox (list): Bounding box as [x1, y1, x2, y2]
    
    Returns:
        float: Width in pixels
    """
    x1, y1, x2, y2 = bbox
    return x2 - x1

def get_bounding_box_center(bbox):
    """
    Compute the center coordinates of the bounding box.
    
    Args:
        bbox (list): Bounding box as [x1, y1, x2, y2]
    
    Returns:
        tuple: (center_x, center_y) in pixels
    """
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y

def compute_object_distance(pixel_width, real_width, focal_length):
    """
    Compute the distance (altitude) of the object from the camera.
    
    Args:
        pixel_width (float): Width of the object in pixels
        real_width (float): Real width of the object in millimeters
        focal_length (float): Focal length of the camera in millimeters
    
    Returns:
        float: Distance in millimeters
    """
    if pixel_width == 0:
        return float('inf')  # Avoid division by zero
    return (real_width * focal_length) / pixel_width

def compute_distance_from_camera(bbox, real_width, focal_length):
    """
    Compute the distance of the pen cap from the camera using its bounding box.
    
    Args:
        bbox (list): Bounding box as [x1, y1, x2, y2]
        real_width (float): Real width of the pen cap in millimeters
        focal_length (float): Focal length of the camera in millimeters
    
    Returns:
        float: Distance in millimeters
    """
    print(f"Bounding box: {bbox}")
    pixel_width = get_bounding_box_width_pixels(bbox)
    print(f"Pixel width: {pixel_width}")
    print(f"Real width: {real_width}")
    return compute_object_distance(pixel_width, real_width, focal_length)

def compute_focal_length(bbox, real_width, distance):
    """
    Compute the focal length of the camera given bounding box, real width, and distance.
    
    Args:
        bbox (list): Bounding box as [x1, y1, x2, y2]
        real_width (float): Real width of the pen cap in millimeters
        distance (float): Distance from camera in millimeters
    
    Returns:
        float: Focal length in millimeters
    """
    pixel_width = get_bounding_box_width_pixels(bbox)
    print(f"Pixel width: {pixel_width}")
    if pixel_width == 0:
        return float('inf')  # Avoid division by zero
    return (pixel_width * distance) / real_width

def compute_real_length(pixel_length, distance, focal_length):
    """
    Compute the real length given pixel length, distance, and focal length.
    
    Args:
        pixel_length (float): Length in pixels
        distance (float): Distance from camera in millimeters
        focal_length (float): Focal length of the camera in millimeters
    
    Returns:
        float: Real length in millimeters
    """
    return (pixel_length * distance) / focal_length

def compute_center_displacements(starting_center, detections, focal_length):
    """
    Compute displacements of object centers from starting position, converted to real mm.
    
    Args:
        starting_location (tuple): (x, y, z) in mm, initial camera/object position
        starting_center (tuple): (center_x, center_y) in pixels, initial center
        detections (list): List of detection dicts with 'box' [x1,y1,x2,y2]
        focal_length (float): Focal length in mm
        distance (float): Distance from camera to object in mm (z from starting_location)
    
    Returns:
        list: List of displacements as (dx_mm, dy_mm) for each detection
    """
    displacements = []
    start_cx, start_cy = starting_center
    
    for det in detections:
        if det is None:
            displacements.append(None)
            continue
        
        bbox = det['box']
        cx, cy = get_bounding_box_center(bbox)
        distance_mm = compute_distance_from_camera(bbox, PHONE_REAL_WIDTH_MM, focal_length)

        # Displacement in pixels
        pixel_dx = cx - start_cx
        pixel_dy = cy - start_cy
        
        # Convert to mm
        real_dx = compute_real_length(pixel_dx, distance_mm, focal_length)
        real_dy = compute_real_length(pixel_dy, distance_mm, focal_length)
        
        displacements.append((real_dx, real_dy))
    
    return displacements





sample_detections = [
    {'label': 'phone', 'score': 0.85, 'box': [40.723670959472656, 874.839111328125, 821.624267578125, 1276.054443359375]},
    {'label': 'phone', 'score': 0.85, 'box': [174.7002716064453, 913.072021484375, 753.0581665039062, 1206.306396484375]},
    {'label': 'phone', 'score': 0.85, 'box': [324.2016296386719, 922.209716796875, 661.7896728515625, 1085.3814697265625]},
]

focal_length = compute_focal_length(
    sample_detections[0]['box'],
    PHONE_REAL_WIDTH_MM,
    330.0
)

print(f"Computed focal length: {focal_length:.2f} mm")

# for idx, det in enumerate(sample_detections):
#     if det is None:
#         print(f"Image {idx + 1}: No detection")
#         continue
    
#     bbox = det['box']
#     center_x, center_y = get_bounding_box_center(bbox)
#     distance_mm = compute_distance_from_camera(bbox, PHONE_REAL_WIDTH_MM, focal_length)
    
    
#     print(f"Image {idx + 1}:")
#     print(f"  Bounding box: {bbox}")
#     print(f"  Center: ({center_x:.1f}, {center_y:.1f}) px")
#     print(f"  Estimated distance: {distance_mm:.2f} mm")



# # Example: compute center displacements
# starting_location = (0, 0, 330)  # Example starting position in mm
# # Use the first detection's center as starting center
# first_det = sample_detections[0]
# if first_det:
#     starting_center = get_bounding_box_center(first_det['box'])
#     displacements = compute_center_displacements(starting_center, sample_detections, focal_length)
    
#     print("\nCenter displacements from starting position:")
#     for idx, disp in enumerate(displacements):
#         if disp is None:
#             print(f"Image {idx + 1}: No detection")
#         else:
#             dx, dy = disp
#             print(f"Image {idx + 1}: Displacement ({dx:.2f}, {dy:.2f}) mm")




