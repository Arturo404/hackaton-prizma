from uuid import uuid4

from integration import get_object_center, get_updated_location
from location_computing import lla_to_ecef, lla_to_xyz, tuple_multiply


flying_sessions = {}

def open_flying_session(starting_location, drone_width_cm, first_frame):
    """
    Simulate opening a flying session with given starting location and focal length.
    
    Args:
        starting_location (tuple): (long, lat, alt)
        drone_width_cm (float): Width of the drone in cm
        first_frame (PIL Image): First frame of the session

    Returns:
        str: Session id
    """

    session_id = uuid4().hex

    starting_center = get_object_center(first_frame)

    current_flying_session = {
        'starting_location_xyz': starting_location,
        'starting_center': starting_center,
        'drone_width_cm': drone_width_cm
    }

    flying_sessions[session_id] = current_flying_session

    print(f"Flying session opened at location {starting_location} with drone width {drone_width_cm} cm")
    return session_id, starting_center


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

    print(f"Updating flying session {session_id}")
    session = flying_sessions[session_id]
    starting_location = session['starting_location_xyz']
    starting_center = session['starting_center']
    drone_width_cm = session['drone_width_cm']
    object_width_mm = drone_width_cm * 10  # Convert cm to mm

    updated_location = get_updated_location(frame, starting_location, object_width_mm, starting_center)
    if updated_location is not None:
        print(f"Updated location: {updated_location}")
    else:
        print("Object detection failed; location not updated.")

    return updated_location, timestamp