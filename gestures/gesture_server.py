import argparse
import asyncio
import websockets
import json
import cv2
import time
import os
from main_controller import MainController
from utils import Event

async def gesture_server(websocket, path):
    print("Gesture client connected")

    # Corrected model paths, assuming the script is run from the project root
    detector_path = "gestures/models/hand_detector.onnx"
    classifier_path = "gestures/models/crops_classifier.onnx"

    if not os.path.exists(detector_path) or not os.path.exists(classifier_path):
        print(f"Error: Model files not found. Expected at {detector_path} and {classifier_path}")
        print("Please ensure you are running the script from the project's root directory.")
        return

    try:
        controller = MainController(detector_path, classifier_path)
    except Exception as e:
        print(f"Error initializing MainController: {e}")
        print("Please ensure ONNX Runtime is installed (`pip install onnxruntime`) and model files are accessible.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    last_gesture_time = 0
    gesture_cooldown = 1.0  # 1-second cooldown to prevent multiple triggers

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            frame = cv2.flip(frame, 1)
            # Process the frame to detect hands and gestures
            controller(frame)

            current_time = time.time()
            # Check for a gesture only if the cooldown period has passed
            if (current_time - last_gesture_time) > gesture_cooldown:
                if len(controller.tracks) > 0:
                    for trk in controller.tracks:
                        # Check for a fresh action from the tracker
                        if trk["tracker"].time_since_update < 1 and trk["hands"].action is not None:
                            action = trk["hands"].action
                            action_to_send = None

                            # Map swipe gestures to commands
                            if Event.SWIPE_LEFT == action or Event.SWIPE_LEFT2 == action or Event.SWIPE_LEFT3 == action or Event.FAST_SWIPE_DOWN == action:
                                action_to_send = "next"
                            elif Event.SWIPE_RIGHT == action or Event.SWIPE_RIGHT2 == action or Event.SWIPE_RIGHT3 == action or Event.FAST_SWIPE_UP == action:
                                action_to_send = "previous"

                            if action_to_send:
                                print(f"Sending action: {action_to_send}")
                                await websocket.send(json.dumps({"type": "gesture", "action": action_to_send}))
                                last_gesture_time = current_time  # Reset cooldown timer
                                trk["hands"].action = None  # Clear the action to prevent re-triggering
                                break  # Process only one gesture per frame loop

            await asyncio.sleep(0.05)  # ~20 FPS processing loop

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred during gesture processing: {e}")
    finally:
        cap.release()
        print("Gesture client disconnected and camera released.")

async def main():
    # Ensure the current working directory is the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root)
    print(f"Running server from directory: {os.getcwd()}")

    async with websockets.serve(gesture_server, "0.0.0.0", 9003):
        print("Gesture WebSocket server started on ws://0.0.0.0:9003")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped manually.")

