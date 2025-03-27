import tkinter as tk

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

        self.cap = cv2.VideoCapture(0)

        width, heigth = 854,480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, heigth)

        self.button1 = tk.Button(self.m, text="Open Camera", command =self.open_camera)
        self.button1.place(x=900, y=1000)

        self.m.mainloop()


    def open_camera(self):
        _, frame = self.cap.read()

        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        captured_image = Image.fromarray(opencv_image)

        photo_image = ImageTk.PhotoImage(image = captured_image)

        self.label_widget.photo_image = photo_image

        self.label_widget.configure(image=photo_image)

        self.label_widget.after(10, self.open_camera)
