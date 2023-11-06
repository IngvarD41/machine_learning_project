import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import os


class IntersectionLabeler:
    def __init__(self, master):
        self.master = master
        self.master.title("Intersection Labeler")

        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack()

        self.image_files = []
        self.current_index = -1

        self.load_button = tk.Button(
            master, text="Open Folder", command=self.load_folder
        )
        self.load_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(
            master, text="Previous", command=self.show_previous
        )
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(master, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(
            master, text="Save Labels", command=self.save_labels
        )
        self.save_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.label_intersection)

        self.labels = []

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.endswith((".jpg", ".png", ".gif"))
            ]
            if self.image_files:
                self.show_next()

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def show_next(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()

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
