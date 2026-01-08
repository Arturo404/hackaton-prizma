import cv2
import os
import argparse
from PIL import Image

def sample_video_frames(video_path, output_folder, sample_rate=1.0, frame_skip=None):
    """
    Sample frames from a video at a specified rate, convert to greyscale, save to folder, and return list of PIL Images.
    
    Args:
        video_path (str): Path to the video file
        output_folder (str): Folder to save sampled frames
        sample_rate (float): Sample every N seconds (e.g., 1.0 for every second)
        frame_skip (int): Alternatively, sample every N frames (overrides sample_rate if set)
    
    Returns:
        list: List of PIL Images (greyscale)
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video FPS: {fps}, Total frames: {total_frames}")
    
    if frame_skip is not None:
        interval = frame_skip
        print(f"Sampling every {frame_skip} frames")
    else:
        interval = int(fps * sample_rate)
        print(f"Sampling every {sample_rate} seconds ({interval} frames)")
    
    frame_count = 0
    saved_count = 0
    pil_images = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % interval == 0:
            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            pil_images.append(pil_img)
            frame_filename = f"frame_{saved_count:04d}.jpg"
            frame_path = os.path.join(output_folder, frame_filename)
            pil_img.save(frame_path)
            saved_count += 1
            print(f"Saved {frame_filename}")

        frame_count += 1
    
    cap.release()
    print(f"Sampling complete. Saved {saved_count} frames to {output_folder}")
    return pil_images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample frames from a video")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("output_folder", help="Folder to save sampled frames")
    parser.add_argument("--sample_rate", type=float, default=1.0, help="Sample every N seconds (default: 1.0)")
    parser.add_argument("--frame_skip", type=int, help="Sample every N frames (overrides sample_rate)")
    
    args = parser.parse_args()
    
    sample_video_frames(args.video_path, args.output_folder, args.sample_rate, args.frame_skip)