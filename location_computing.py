# Configuration for pen cap and camera
PEN_CAP_REAL_WIDTH_MM = 20.0  # Real width of the pen cap in millimeters (adjust as needed)
CAMERA_FOCAL_LENGTH_MM = 26.0  # Focal length of the camera in millimeters (adjust as needed)

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

def compute_pen_cap_distance(bbox, real_width, focal_length):
    """
    Compute the distance of the pen cap from the camera using its bounding box.
    
    Args:
        bbox (list): Bounding box as [x1, y1, x2, y2]
        real_width (float): Real width of the pen cap in millimeters
        focal_length (float): Focal length of the camera in millimeters
    
    Returns:
        float: Distance in millimeters
    """
    pixel_width = get_bounding_box_width_pixels(bbox)
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

# Example usage with detection results
# To use real detections, run the cells from pen_cap_detection.ipynb first
# or copy the get_object_bounding_box function and detections here.

# Assuming detections from pen_cap_detection.ipynb
# For demonstration, let's assume some sample detections
sample_detections = [
    {'label': 'pen cap', 'score': 0.85, 'box': [644.2440185546875, 569.2691040039062, 767.0145263671875, 1077.2977294921875]},
    {'label': 'pen cap', 'score': 0.92, 'box': [699.7681884765625, 953.6226196289062, 726.6387329101562, 1062.0035400390625]},
    None,  # No detection
    {'label': 'pen cap', 'score': 0.78, 'box': [679.7200317382812, 1296.2269287109375, 708.9035034179688, 1422.017578125]},
    {'label': 'pen cap', 'score': 0.78, 'box': [716.9485473632812, 780.4949951171875, 733.974609375, 831.747314453125]},
    {'label': 'pen cap', 'score': 0.78, 'box': [548.505615234375, 790.5347900390625, 673.2413330078125, 1317.199951171875]}
]

for idx, det in enumerate(sample_detections):
    if det is None:
        print(f"Image {idx + 1}: No detection")
        continue
    
    bbox = det['box']
    center_x, center_y = get_bounding_box_center(bbox)
    distance_mm = compute_pen_cap_distance(bbox, PEN_CAP_REAL_WIDTH_MM, CAMERA_FOCAL_LENGTH_MM)
    
    
    print(f"Image {idx + 1}:")
    print(f"  Bounding box: {bbox}")
    print(f"  Center: ({center_x:.1f}, {center_y:.1f}) px")
    print(f"  Estimated distance: {distance_mm:.2f} mm")
    
    # Example: compute real height if we had pixel height
    pixel_height = bbox[3] - bbox[1]  # y2 - y1
    real_height_mm = compute_real_length(pixel_height, distance_mm, CAMERA_FOCAL_LENGTH_MM)
    print(f"  Pixel height: {pixel_height:.2f} px -> Real height: {real_height_mm:.2f} mm")
    print()

# Additional example: compute focal length
focal_length_computed = compute_focal_length([548.505615234375, 790.5347900390625, 673.2413330078125, 1317.199951171875], PEN_CAP_REAL_WIDTH_MM, 146)
print(f"  Computed focal length: {focal_length_computed:.2f} mm")