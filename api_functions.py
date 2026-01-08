from uuid import uuid4

from integration import get_object_center, get_updated_location


flying_sessions = {}

def open_flying_session(starting_location, drone_width_cm, first_frame):
    """
    Simulate opening a flying session with given starting location and focal length.
    
    Args:
        starting_location (tuple): (x, y, z) in mm
        focal_length (float): Focal length in mm
        :param starting_location:
        :param drone_width_cm:
        :param first_frame:

    Returns:
        str: Session info
    """

    session_id = uuid4().hex

    starting_center = get_object_center(first_frame)

    current_flying_session = {
        'starting_location': starting_location,
        'starting_center': starting_center,
        'drone_width_cm': drone_width_cm
    }

    flying_sessions[session_id] = current_flying_session

    print(f"Flying session opened at location {starting_location} with drone width {drone_width_cm} cm")
    return session_id, starting_location


def update_flying_session(session_id, frame, timestamp):
    """
    Update flying session with new frame, compute updated location.
    
    Args:
        session_id (str): Session identifier
        frame (PIL Image): Current frame
        timestamp (float): Timestamp of the frame
    
    Returns:
        tuple: Updated location (x, y, z) in mm or None if detection failed
    """
    if session_id not in flying_sessions:
        print(f"Session ID {session_id} not found")
        return None

    session = flying_sessions[session_id]
    starting_location = session['starting_location']
    starting_center = session['starting_center']
    drone_width_cm = session['drone_width_cm']
    object_width_mm = drone_width_cm * 10  # Convert cm to mm

    updated_location = get_updated_location(frame, starting_location, object_width_mm, starting_center)
    if updated_location is not None:
        print(f"Updated location: {updated_location}")
    else:
        print("Object detection failed; location not updated.")

    return updated_location, timestamp