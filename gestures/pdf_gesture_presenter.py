import argparse
import time
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

from main_controller import MainController
from utils import Drawer, Event, targets


class PDFGesturePresenter:
    """
    A GUI application that displays a PDF presentation on one side and
    a camera feed with hand gesture recognition on the other side.
    Gestures control the PDF navigation.
    """

    def __init__(self, root, args):
        self.root = root
        self.root.title("PDF Gesture Presenter")

        # Initialize variables
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_path = None

        # Gesture controller
        self.controller = MainController(args.detector, args.classifier)
        self.drawer = Drawer()
        self.debug_mode = args.debug

        # Gesture cooldown to prevent multiple triggers
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # Reduced to 0.5 second cooldown for better responsiveness

        # Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Performance optimization: cache target size
        self.cached_width = None
        self.cached_height = None

        # Set up GUI
        self.setup_gui()

        # Load PDF if provided
        if args.pdf:
            self.load_pdf(args.pdf)

        # Start the update loop
        self.is_running = True
        self.update()

    def setup_gui(self):
        """Set up the GUI layout."""
        # Configure window
        self.root.geometry("1600x900")

        # Top menu frame
        menu_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        menu_frame.pack(side=tk.TOP, fill=tk.X)

        # Load PDF button
        load_btn = tk.Button(
            menu_frame,
            text="Load PDF",
            command=self.browse_pdf,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        )
        load_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Page info label
        self.page_info_label = tk.Label(
            menu_frame,
            text="No PDF loaded",
            bg='#2c3e50',
            fg='white',
            font=('Arial', 12)
        )
        self.page_info_label.pack(side=tk.LEFT, padx=20)

        # Instructions label
        instructions = tk.Label(
            menu_frame,
            text="Gestures: Fast Swipe UP (Previous) | Fast Swipe DOWN (Next)",
            bg='#2c3e50',
            fg='#ecf0f1',
            font=('Arial', 10)
        )
        instructions.pack(side=tk.RIGHT, padx=20)

        # Main content frame
        content_frame = tk.Frame(self.root, bg='#34495e')
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # PDF display frame (left side)
        pdf_frame = tk.Frame(content_frame, bg='#2c3e50', relief=tk.SUNKEN, borderwidth=2)
        pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # PDF canvas
        self.pdf_canvas = tk.Canvas(pdf_frame, bg='white')
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)

        # Camera display frame (right side)
        camera_frame = tk.Frame(content_frame, bg='#2c3e50', relief=tk.SUNKEN, borderwidth=2)
        camera_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Camera title label
        camera_title = tk.Label(
            camera_frame,
            text="Camera Feed - Hand Gesture Recognition",
            bg='#2c3e50',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        camera_title.pack(pady=5)

        # Camera label for video feed
        self.camera_label = tk.Label(
            camera_frame,
            text="Camera feed is in a separate window.\nPress 'q' in that window to quit.",
            bg='black',
            fg='white',
            font=('Arial', 14),
            justify=tk.CENTER
        )
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Navigation buttons at bottom
        nav_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Previous page button
        prev_btn = tk.Button(
            nav_frame,
            text="◄ Previous",
            command=self.previous_page,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=15,
            pady=5
        )
        prev_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Next page button
        next_btn = tk.Button(
            nav_frame,
            text="Next ►",
            command=self.next_page,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=15,
            pady=5
        )
        next_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.previous_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Escape>', lambda e: self.close_application())

    def browse_pdf(self):
        """Open file dialog to select a PDF."""
        filename = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.load_pdf(filename)

    def load_pdf(self, pdf_path):
        """Load a PDF file."""
        try:
            if self.pdf_document:
                self.pdf_document.close()

            self.pdf_document = fitz.open(pdf_path)
            self.pdf_path = pdf_path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0

            self.update_page_info()
            self.display_pdf_page()

            print(f"Loaded PDF: {pdf_path} ({self.total_pages} pages)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            print(f"Error loading PDF: {e}")

    def display_pdf_page(self):
        """Display the current PDF page."""
        if not self.pdf_document or self.current_page >= self.total_pages:
            return

        try:
            page = self.pdf_document[self.current_page]

            # Get canvas dimensions
            canvas_width = self.pdf_canvas.winfo_width()
            canvas_height = self.pdf_canvas.winfo_height()

            # Use default size if canvas not yet rendered
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600

            # Calculate zoom to fit page in canvas
            page_rect = page.rect
            zoom_x = canvas_width / page_rect.width
            zoom_y = canvas_height / page_rect.height
            zoom = min(zoom_x, zoom_y) * 0.95  # 95% to leave some margin

            # Render page to pixmap
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            # Convert to PhotoImage for Tkinter
            self.pdf_image = ImageTk.PhotoImage(img)

            # Display on canvas
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.pdf_image,
                anchor=tk.CENTER
            )

        except Exception as e:
            print(f"Error displaying PDF page: {e}")

    def next_page(self):
        """Go to next page."""
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_info()
            self.display_pdf_page()
            print(f"Next page: {self.current_page + 1}/{self.total_pages}")

    def previous_page(self):
        """Go to previous page."""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.update_page_info()
            self.display_pdf_page()
            print(f"Previous page: {self.current_page + 1}/{self.total_pages}")

    def update_page_info(self):
        """Update the page information label."""
        if self.pdf_document:
            self.page_info_label.config(
                text=f"Page {self.current_page + 1} / {self.total_pages}"
            )
        else:
            self.page_info_label.config(text="No PDF loaded")

    def process_gestures(self, frame):
        """Process hand gestures and trigger actions."""
        start_time = time.time()
        bboxes, ids, labels = self.controller(frame)

        # Draw debug information
        if self.debug_mode:
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
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Process gestures
        if len(self.controller.tracks) > 0:
            for trk in self.controller.tracks:
                if trk["tracker"].time_since_update < 1 and trk["hands"].action is not None:
                    action = trk["hands"].action
                    current_time = time.time()

                    # Check if enough time has passed since last gesture
                    if current_time - self.last_gesture_time > self.gesture_cooldown:

                        # Fast swipe down = Next slide
                        if action == Event.FAST_SWIPE_DOWN:
                            print(f"Gesture detected: Next Slide (Action: {action.name})")
                            self.next_page()
                            self.last_gesture_time = current_time
                            self.drawer.set_action(action)

                        # Fast swipe up = Previous slide
                        elif action == Event.FAST_SWIPE_UP:
                            print(f"Gesture detected: Previous Slide (Action: {action.name})")
                            self.previous_page()
                            self.last_gesture_time = current_time
                            self.drawer.set_action(action)

                        # Handle other gestures for visual feedback
                        elif action in [Event.SWIPE_LEFT, Event.SWIPE_LEFT2, Event.SWIPE_LEFT3]:
                            self.drawer.set_action(action)
                        elif action in [Event.SWIPE_RIGHT, Event.SWIPE_RIGHT2, Event.SWIPE_RIGHT3]:
                            self.drawer.set_action(action)
                        elif action in [Event.SWIPE_UP, Event.SWIPE_UP2, Event.SWIPE_UP3]:
                            self.drawer.set_action(action)
                        elif action in [Event.SWIPE_DOWN, Event.SWIPE_DOWN2, Event.SWIPE_DOWN3]:
                            self.drawer.set_action(action)
                        elif action in [Event.DRAG, Event.DRAG2, Event.DRAG3]:
                            self.drawer.set_action(action)
                        elif action in [Event.DROP, Event.DROP2, Event.DROP3]:
                            self.drawer.set_action(action)
                        elif action in [Event.ZOOM_IN, Event.ZOOM_OUT, Event.DOUBLE_TAP, Event.TAP]:
                            self.drawer.set_action(action)
                    else:
                        # Still in cooldown, but acknowledge the gesture was detected
                        if action in [Event.FAST_SWIPE_UP, Event.FAST_SWIPE_DOWN]:
                            print(f"Gesture detected but in cooldown period ({self.gesture_cooldown - (current_time - self.last_gesture_time):.1f}s remaining)")

                    # Clear the action after processing
                    trk["hands"].action = None

        if self.debug_mode:
            frame = self.drawer.draw(frame)

        return frame

    def update(self):
        """Update loop for camera feed and gesture processing."""
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Process gestures
            frame = self.process_gestures(frame)

            # Display the frame in a separate OpenCV window for high performance
            cv2.imshow("Camera Feed", frame)

            # Check for 'q' key press in the OpenCV window to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close_application()
                return

        # Schedule the next update
        self.root.after(1, self.update)

    def close_application(self):
        """Clean up and close the application."""
        self.is_running = False
        self.cap.release()
        cv2.destroyAllWindows()  # Close the OpenCV window
        if self.pdf_document:
            self.pdf_document.close()
        self.root.quit()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="PDF Gesture Presenter with Hand Tracking")
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
        "--pdf",
        default=None,
        type=str,
        help="Path to PDF file to load on startup."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to see bounding boxes and FPS."
    )

    args = parser.parse_args()

    # Create Tkinter root window
    root = tk.Tk()

    # Create and run the application
    app = PDFGesturePresenter(root, args)

    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", app.close_application)

    # Start the GUI main loop
    root.mainloop()


if __name__ == "__main__":
    main()
