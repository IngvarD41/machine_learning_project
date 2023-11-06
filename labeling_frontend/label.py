import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import imageio


class IntersectionLabeler:
    def __init__(self, master):
        self.master = master
        self.master.title("Intersection Labeler")

        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        self.image = None
        self.intersections = []

        self.load_button = tk.Button(master, text="Open Image", command=self.load_image)
        self.load_button.pack()

        self.save_button = tk.Button(
            master, text="Save Labels", command=self.save_labels
        )
        self.save_button.pack()

        self.canvas.bind("<Button-1>", self.label_intersection)

    def load_image(self):
        ...

    def label_intersection(self, event):
        ...

    def save_labels(self):
        ...


if __name__ == "__main__":
    root = tk.Tk()
    app = IntersectionLabeler(root)
    root.mainloop()
