import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import cv2 as cv
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

        self.cap = cv.VideoCapture(0)
        self.camera_started = False

        width, heigth = 854, 480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, heigth)

        self.button1 = tk.Button(self.m, text="Open Camera", command =self.open_camera)
        self.button1.place(x=350, y=500)

        self.button2 = tk.Button(self.m, text="Take a picture", command=self.take_picture)
        self.button2.place(x=450, y=500)

        self.button3 = tk.Button(self.m, text="Choose a photo for the model", command = self.open_file_explorer)
        self.button3.place(x=1400, y =1020)

        self.m.mainloop()


    def open_camera(self):
        self.camera_started = True

        _, frame = self.cap.read()

        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        captured_image = Image.fromarray(opencv_image)

        photo_image = ImageTk.PhotoImage(image = captured_image)

        self.label_widget.photo_image = photo_image

        self.label_widget.configure(image=photo_image)

        self.label_widget.after(10, self.open_camera)

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