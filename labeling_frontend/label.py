import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import os
import imageio
from PIL import Image, ImageTk


class IntersectionLabeler:
    def __init__(self, master):
        self.master = master
        self.master.title("Intersection Labeler")

        self.canvas = tk.Canvas(master, width=1000, height=1000)
        self.canvas.pack(side=tk.TOP)

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

        self.coordinates_label = tk.Label(master, text="Coordinates: (0, 0)")
        self.coordinates_label.pack(side=tk.LEFT)

        self.canvas.bind("<Motion>", self.update_coordinates)

        self.labels = []

        self.text_window = tk.Toplevel(self.master)
        self.text_window.title("Text Messages")
        self.text = tk.Text(self.text_window, height=20, width=80)
        self.text.pack()

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.endswith((".gif"))
            ]
            if self.image_files:
                self.show_next()
            self.show_text_message(f"Loaded folder: {folder_path}")
            self.show_text_message(f"{len(self.image_files)} images total")

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def show_next(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()

    def load_image(self):
        self.labels = []  # Clear previously recorded labels
        path = self.image_files[self.current_index]

        if path.lower().endswith(".gif"):
            self.load_gif(path)
        else:
            self.show_text_message("EPIC FAIL")

    def load_gif(self, path):
        self.gif = imageio.mimread(path)
        self.frame_index = 0
        self.image = self.gif[self.frame_index]
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        self.display_image()

    def display_image(self):
        if hasattr(self, "tk_image"):
            self.canvas.delete(self.tk_image)

        height, width, channels = self.image.shape
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(self.image))
        self.canvas.create_image(
            height // 2, width // 2, anchor=tk.CENTER, image=self.tk_image
        )

    def label_intersection(self, event):
        try:
            if self.image is not None:
                x = event.x
                y = 1000 - event.y
                self.labels.append((x, y))
                cv2.circle(self.image, (event.x, event.y), 5, (255, 0, 0), -1)
                self.display_image()
        except Exception as e:
            self.show_text_message(f"An error occurred: {e}")

    def update_coordinates(self, event):
        x = event.x
        y = 1000 - event.y
        self.coordinates_label.config(text=f"Coordinates: ({x}, {y})")

    def save_labels(self):
        try:
            filename = f"coordinates_test.txt"
            image_name = os.path.basename(self.image_files[self.current_index])
            image_name = image_name.removesuffix(".gif").removeprefix("map_")

            with open(filename, "a") as f:
                f.write(f"{image_name}, ")

                if self.labels:
                    coordinates = [f"{x}-{y}" for x, y in self.labels]
                    result = ", ".join(coordinates)
                    f.write(result + "\n")
                else:
                    result = "None"
                    f.write(result + "\n")

            self.show_text_message(f"Labels saved for {image_name}: {result}")

        except Exception as e:
            self.show_text_message(f"An error occurred: {e}")

    def show_text_message(self, message):
        self.text.insert(tk.END, message + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = IntersectionLabeler(root)
    root.mainloop()
