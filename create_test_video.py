"""
Create a simple test video with text overlays and scene changes
Perfect for testing SmolVLM's ability to detect changes
No audio required - purely visual test
"""

import cv2
import numpy as np

def create_frame(text, bg_color, text_color=(255, 255, 255)):
    """Create a simple frame with text"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = bg_color
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 3
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Center text
    x = (640 - text_width) // 2
    y = (480 + text_height) // 2
    
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)
    
    return frame

def main():
    output_file = "test_visual.mp4"
    fps = 15
    duration_per_scene = 3  # seconds per scene
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (640, 480))
    
    # Define scenes
    scenes = [
        ("PERSON ENTERS ROOM", (50, 50, 150)),      # Dark blue
        ("PERSON SITS DOWN", (50, 150, 50)),        # Dark green
        ("PERSON STANDS UP", (150, 50, 50)),        # Dark red
        ("PERSON WAVES HAND", (150, 100, 50)),      # Orange
        ("PERSON LEAVES ROOM", (100, 50, 150)),     # Purple
    ]
    
    frames_per_scene = fps * duration_per_scene
    
    print(f"🎬 Creating test video: {output_file}")
    print(f"   Scenes: {len(scenes)}")
    print(f"   Duration: {len(scenes) * duration_per_scene} seconds")
    print(f"   FPS: {fps}")
    
    for i, (text, color) in enumerate(scenes):
        print(f"   Scene {i+1}/{len(scenes)}: {text}")
        frame = create_frame(text, color)
        
        for _ in range(frames_per_scene):
            out.write(frame)
    
    out.release()
    print(f"✅ Video created: {output_file}")
    print(f"\n🎯 Test with:")
    print(f"   python main_video.py {output_file} --frames 10 --no-audio")

if __name__ == "__main__":
    main()
