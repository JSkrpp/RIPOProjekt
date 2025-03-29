import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import cv2 as cv
import platform
import subprocess
import pygrabber
from PIL import Image, ImageTk

class Interface:

    def __init__(self):
        self.m = tk.Tk()
        self.m.geometry("1920x1080")
        self.m.minsize(1920, 1080)
        self.m.maxsize(1920,1080)
        self.m.bind('<Escape>', lambda e: self.m.quit())

        self.label_widget = tk.Label(self.m, width=854, height=480)
        self.label_widget.place(x=0, y=10)
        self.photo_widget = tk.Label(self.m, width=854, height=480)
        self.photo_widget.place(x=1000, y=10)
        self.model_widget = tk.Label(self.m, width=854, height=480)
        self.model_widget.place(x=1000, y=530)

        self.cap = None
        self.camera_started = False

        # Find available cameras
        self.available_cameras = self.get_available_cameras()
        self.selected_camera = tk.StringVar(self.m)
        self.selected_camera.set(self.available_cameras[0][0])

        self.camera_menu = tk.OptionMenu(self.m, self.selected_camera, *[name for name, _ in self.available_cameras])
        self.camera_menu.place(x=150, y=500)

        self.button1 = tk.Button(self.m, text="Open Camera", command =self.open_camera)
        self.button1.place(x=350, y=500)

        self.button2 = tk.Button(self.m, text="Take a picture", command=self.take_picture)
        self.button2.place(x=450, y=500)

        self.button3 = tk.Button(self.m, text="Choose a photo for the model", command = self.open_file_explorer)
        self.button3.place(x=1400, y =1020)

        self.m.mainloop()

    def open_camera(self):
        selected_name = self.selected_camera.get()
        cam_index = None

        for name, index in self.available_cameras:
            if name == selected_name:
                cam_index = int(index)
                break

        if cam_index is None:
            messagebox.showwarning("Warning", "No available cameras detected!")
            return

        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Failed to open {selected_name}")
            return

        width, heigth = 854, 480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, heigth)

        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Failed to open camera {cam_index}")
            return

        self.camera_started = True
        self.update_camera_frame()

    def open_file_explorer(self):
        # Open file explorer to select an image file
        file_path = tk.filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff"), ("All Files", "*.*"))
        )

        if file_path:
            # Load and display the selected image
            selected_image = Image.open(file_path)
            selected_image = selected_image.resize((854, 480))  # Resize image to fit the label widget
            photo_image = ImageTk.PhotoImage(selected_image)

            self.model_widget.photo_image = photo_image
            self.model_widget.configure(image=photo_image)

    def take_picture(self):
        if not self.camera_started:
            messagebox.showwarning("Warning", "Camera output has not been started yet!")
            return

        if self.cap and self.cap.isOpened():
            _, frame = self.cap.read()
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)

            # Resize for the photo widget
            captured_image_resized = captured_image.resize((854, 480))
            photo_image = ImageTk.PhotoImage(image=captured_image_resized)

            self.photo_widget.photo_image = photo_image
            self.photo_widget.configure(image=photo_image)

    def get_available_cameras(self):
        available_cameras = []

        system = platform.system()

        if system == "Windows":
            # Windows: Use pygrabber to get camera names
            try:
                from pygrabber.dshow_graph import FilterGraph
                graph = FilterGraph()
                camera_list = graph.get_input_devices()
                for i, name in enumerate(camera_list):
                    available_cameras.append((name, str(i)))  # (Camera Name, Index)
            except ImportError:
                print("Install pygrabber: pip install pygrabber")
                available_cameras = [(f"Camera {i}", str(i)) for i in range(10)]

        elif system == "Linux":
            # Linux: Use v4l2-ctl command to get camera names
            try:
                result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True)
                lines = result.stdout.split("\n")
                index = None
                for line in lines:
                    if "usb" in line.lower() or "camera" in line.lower():
                        camera_name = line.strip()
                    elif "/dev/video" in line:
                        index = line.strip()[-1]
                        available_cameras.append((camera_name, index))
            except FileNotFoundError:
                print("v4l2-ctl not found. Install with: sudo apt install v4l-utils")
                available_cameras = [(f"Camera {i}", str(i)) for i in range(10)]

        else:
            # Default fallback for unsupported OS
            available_cameras = [(f"Camera {i}", str(i)) for i in range(10)]

        return available_cameras if available_cameras else [("No Camera Found", "0")]

    def update_camera_frame(self):
        if self.cap and self.cap.isOpened():
            _, frame = self.cap.read()
            if frame is None:
                return

            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)

            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)

            self.label_widget.after(10, self.update_camera_frame)