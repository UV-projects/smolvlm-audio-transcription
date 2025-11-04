#!/usr/bin/env python3
"""
Gesture Diagnostic Tool
This script helps debug gesture recognition by showing detailed information
about what the system is detecting.
"""
import argparse
import time
import cv2
import numpy as np

from main_controller import MainController
from utils import Drawer, Event, targets


def run_diagnostics(args):
    """Run gesture diagnostics with verbose output."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    controller = MainController(args.detector, args.classifier)
    drawer = Drawer()

    print("\n" + "="*60)
    print("GESTURE DIAGNOSTIC MODE")
    print("="*60)
    print("\nThis tool will show you what gestures are being detected.")
    print("\nInstructions:")
    print("  1. Make sure your hand is visible in the camera")
    print("  2. Try making clear swipe gestures")
    print("  3. Watch the terminal for detection messages")
    print("  4. Press 'q' in the camera window to quit")
    print("\nSwipe Gestures:")
    print("  - Swipe RIGHT to LEFT (→ to ←) should trigger SWIPE_LEFT")
    print("  - Swipe LEFT to RIGHT (← to →) should trigger SWIPE_RIGHT")
    print("\n" + "="*60 + "\n")

    frame_count = 0
    gesture_count = {
        'FAST_SWIPE_DOWN': 0,
        'FAST_SWIPE_UP': 0,
        'SWIPE_UP': 0,
        'SWIPE_DOWN': 0,
        'SWIPE_LEFT': 0,
        'SWIPE_RIGHT': 0,
        'OTHER': 0
    }

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Flip the frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        frame_count += 1

        start_time = time.time()
        bboxes, ids, labels = controller(frame)

        # Draw bounding boxes and labels
        if bboxes is not None:
            bboxes = bboxes.astype(np.int32)
            for i in range(bboxes.shape[0]):
                box = bboxes[i, :]
                gesture = targets[labels[i]] if labels[i] is not None else "None"

                # Draw box
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 255), 3)

                # Draw label with background
                label_text = f"ID {ids[i]}: {gesture}"
                (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(frame, (box[0], box[1] - text_height - 10),
                            (box[0] + text_width, box[1]), (0, 255, 255), -1)
                cv2.putText(frame, label_text, (box[0], box[1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Calculate and show FPS
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show number of tracks
        num_tracks = len(controller.tracks)
        cv2.putText(frame, f"Tracks: {num_tracks}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Process gestures and show detailed info
        if num_tracks > 0:
            for trk_idx, trk in enumerate(controller.tracks):
                time_since_update = trk["tracker"].time_since_update
                action = trk["hands"].action

                # Show track info on frame
                info_y = 110 + (trk_idx * 40)
                track_info = f"Track {trk_idx}: Update={time_since_update}"
                cv2.putText(frame, track_info, (10, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                if time_since_update < 1 and action is not None:
                    action_name = action.name if action else "None"

                    # Print to terminal
                    print(f"\n>>> GESTURE DETECTED! <<<")
                    print(f"    Frame: {frame_count}")
                    print(f"    Track ID: {trk_idx}")
                    print(f"    Action: {action_name}")
                    print(f"    Time: {time.strftime('%H:%M:%S')}")

                    # Update counters
                    if action_name == 'FAST_SWIPE_DOWN':
                        gesture_count['FAST_SWIPE_DOWN'] += 1
                        print(f"    >>> THIS SHOULD TRIGGER: NEXT SLIDE <<<")
                    elif action_name == 'FAST_SWIPE_UP':
                        gesture_count['FAST_SWIPE_UP'] += 1
                        print(f"    >>> THIS SHOULD TRIGGER: PREVIOUS SLIDE <<<")
                    elif 'SWIPE_UP' in action_name:
                        gesture_count['SWIPE_UP'] += 1
                    elif 'SWIPE_DOWN' in action_name:
                        gesture_count['SWIPE_DOWN'] += 1
                    elif 'SWIPE_LEFT' in action_name:
                        gesture_count['SWIPE_LEFT'] += 1
                    elif 'SWIPE_RIGHT' in action_name:
                        gesture_count['SWIPE_RIGHT'] += 1
                    else:
                        gesture_count['OTHER'] += 1

                    # Show on frame
                    cv2.putText(frame, f"ACTION: {action_name}", (10, info_y + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    # Draw the gesture visualization
                    drawer.set_action(action)
                    trk["hands"].action = None

        # Draw gesture visualization
        frame = drawer.draw(frame)

        # Show gesture counts
        count_y = frame.shape[0] - 150
        cv2.putText(frame, "Gesture Counts:", (10, count_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"FAST DOWN (Next): {gesture_count['FAST_SWIPE_DOWN']}", (10, count_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"FAST UP (Prev): {gesture_count['FAST_SWIPE_UP']}", (10, count_y + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Regular Swipes: {gesture_count['SWIPE_UP'] + gesture_count['SWIPE_DOWN'] + gesture_count['SWIPE_LEFT'] + gesture_count['SWIPE_RIGHT']}", (10, count_y + 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"Other: {gesture_count['OTHER']}", (10, count_y + 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display instructions
        cv2.putText(frame, "Press 'q' to quit", (frame.shape[1] - 250, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Gesture Diagnostic Tool", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Show summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"\nTotal frames processed: {frame_count}")
    print(f"\nSlide Control Gestures:")
    print("="*60)
    print(f"\nTotal frames processed: {frame_count}")
    print(f"\nGesture detections:")
    print(f"  SWIPE_LEFT (Next slide):     {gesture_count['SWIPE_LEFT']}")
    print(f"  SWIPE_RIGHT (Previous slide): {gesture_count['SWIPE_RIGHT']}")
    print(f"  SWIPE_UP:                     {gesture_count['SWIPE_UP']}")
    print(f"  SWIPE_DOWN:                   {gesture_count['SWIPE_DOWN']}")
    print(f"  OTHER gestures:               {gesture_count['OTHER']}")
    print("\n" + "="*60 + "\n")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gesture Recognition Diagnostic Tool")
    parser.add_argument(
        "--detector",
        default='gestures/models/hand_detector.onnx',
        type=str,
        help="Path to the hand detector ONNX model."
    )
    parser.add_argument(
        "--classifier",
        default='gestures/models/crops_classifier.onnx',
        type=str,
        help="Path to the gesture classifier ONNX model."
    )
    args = parser.parse_args()
    run_diagnostics(args)

