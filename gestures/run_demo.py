import argparse
import time

import cv2
import numpy as np

# --- ADDED IMPORT ---
# Import the keyboard controller from the pynput library to simulate key presses.
from pynput.keyboard import Key, Controller as KeyboardController

from main_controller import MainController
from utils import Drawer, Event, targets


def run(args):
    """
    Main function to run the gesture recognition demo.
    Initializes video capture, the main controller, and the keyboard controller.
    Enters a loop to process video frames and trigger actions based on detected gestures.
    """
    cap = cv2.VideoCapture(0)
    # Set a common camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    controller = MainController(args.detector, args.classifier)
    drawer = Drawer()
    debug_mode = args.debug

    # --- ADDED INITIALIZATION ---
    # Create an instance of the keyboard controller.
    keyboard = KeyboardController()

    print("Starting gesture control. Make your PDF viewer the active window.")
    print("Swipe from Right to Left for NEXT slide (Right Arrow).")
    print("Swipe from Left to Right for PREVIOUS slide (Left Arrow).")
    print("Press 'q' in the camera window to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Flip the frame horizontally for a more intuitive "mirror" effect
        frame = cv2.flip(frame, 1)

        start_time = time.time()
        bboxes, ids, labels = controller(frame)

        if debug_mode:
            if bboxes is not None:
                bboxes = bboxes.astype(np.int32)
                for i in range(bboxes.shape[0]):
                    box = bboxes[i, :]
                    gesture = targets[labels[i]] if labels[i] is not None else "None"

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 255, 0), 4)
                    cv2.putText(
                        frame,
                        f"ID {ids[i]} : {gesture}",
                        (box[0], box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

            fps = 1.0 / (time.time() - start_time)
            cv2.putText(frame, f"fps {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if len(controller.tracks) > 0:
            for trk in controller.tracks:
                if trk["tracker"].time_since_update < 1 and trk["hands"].action is not None:

                    # --- MODIFIED SECTION FOR PDF CONTROL ---

                    # A swipe from right to left triggers the RIGHT arrow key (NEXT slide)
                    if Event.SWIPE_LEFT == trk["hands"].action or Event.SWIPE_LEFT2 == trk[
                        "hands"].action or Event.SWIPE_LEFT3 == trk["hands"].action:
                        print("Action: Next Slide")
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None

                    # A swipe from left to right triggers the LEFT arrow key (PREVIOUS slide)
                    elif Event.SWIPE_RIGHT == trk["hands"].action or Event.SWIPE_RIGHT2 == trk[
                        "hands"].action or Event.SWIPE_RIGHT3 == trk["hands"].action:
                        print("Action: Previous Slide")
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None

                    # --- END OF MODIFIED SECTION ---

                    # Keep the other original gesture actions for visual feedback if debug mode is on
                    elif Event.SWIPE_UP == trk["hands"].action or Event.SWIPE_UP2 == trk[
                        "hands"].action or Event.SWIPE_UP3 == trk["hands"].action:
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None
                    elif Event.SWIPE_DOWN == trk["hands"].action or Event.SWIPE_DOWN2 == trk[
                        "hands"].action or Event.SWIPE_DOWN3 == trk["hands"].action:
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None
                    elif trk["hands"].action in [Event.DRAG, Event.DRAG2, Event.DRAG3]:
                        drawer.set_action(trk["hands"].action)
                    elif trk["hands"].action in [Event.DROP, Event.DROP2, Event.DROP3]:
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None
                    elif trk["hands"].action in [Event.FAST_SWIPE_DOWN, Event.FAST_SWIPE_UP, Event.ZOOM_IN,
                                                 Event.ZOOM_OUT, Event.DOUBLE_TAP, Event.TAP]:
                        drawer.set_action(trk["hands"].action)
                        trk["hands"].action = None

        if debug_mode:
            frame = drawer.draw(frame)

        cv2.imshow("Gesture Control Camera Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run dynamic gesture control demo.")
    parser.add_argument(
        "--detector",
        default='models/hand_detector.onnx',
        type=str,
        help="Path to the hand detector ONNX model."
    )
    parser.add_argument(
        "--classifier",
        default='models/crops_classifier.onnx',
        type=str,
        help="Path to the gesture classifier ONNX model."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to see bounding boxes and FPS."
    )
    args = parser.parse_args()
    run(args)
