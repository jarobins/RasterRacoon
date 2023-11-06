import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

class RasterImageDisplay:
    def __init__(self, root, width=256, height=256):
        self.root = root
        self.width = width
        self.height = height
        self.scale_factor = 4
        self.canvas_width = 512  # Set the canvas size
        self.canvas_height = 512
        
        # Toolbar frame
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Canvas for image display with scrollbars
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', width=self.canvas_width, height=self.canvas_height, scrollregion=(0, 0, self.width, self.height))
        self.hbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Initial binary data and image
        self.binary_data = None
        self.image = None
        self.tk_image = None
        
        # Add toolbar widgets
        self.add_toolbar_widgets()

    def load_binary_data(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                self.binary_data = file.read()
                self.refresh_image()

    def binary_to_image(self, binary_data, width):
        # Calculate the height based on the data length and width; pad the data if necessary
        height = (len(binary_data) + width - 1) // width  # Ceiling division
        padded_length = height * width
        binary_data = binary_data.ljust(padded_length, b'\x00')  # Pad the data
        
        image_array = np.frombuffer(binary_data, dtype=np.uint8).reshape((height, width))
        return Image.fromarray(image_array)

    def refresh_image(self):
        if self.binary_data:
            try:
                self.image = self.binary_to_image(self.binary_data, self.width)
                self.update_image_scale()
                self.canvas.config(scrollregion=(0, 0, self.width * self.scale_factor, self.image.height * self.scale_factor))
            except ValueError as e:
                print(f"Error: {e}. Please check the width and the binary data size.")

    def update_image_scale(self):
        if self.image:
            scaled_image = self.image.resize((int(self.width * self.scale_factor), int(self.image.height * self.scale_factor)), Image.NEAREST)
            self.tk_image = ImageTk.PhotoImage(scaled_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def change_width(self):
        try:
            new_width = int(self.width_entry.get())
            self.width = new_width
            self.refresh_image()
        except ValueError:
            print("Please enter a valid width.")

    def add_toolbar_widgets(self):
        tk.Button(self.toolbar, text="Load Binary File", command=self.load_binary_data).pack(pady=2)
        
        # Entry for raster width
        tk.Label(self.toolbar, text="Raster Width:").pack(pady=2)
        self.width_entry = tk.Entry(self.toolbar)
        self.width_entry.pack(pady=2)
        self.width_entry.insert(0, str(self.width))
        
        tk.Button(self.toolbar, text="Set Width", command=self.change_width).pack(pady=2)
        
        # Scale for image zoom
        self.scale = tk.Scale(self.toolbar, from_=1.0, to=16.0, resolution=1.0, orient=tk.HORIZONTAL, label="Scale", command=self.set_scale)
        self.scale.set(self.scale_factor)
        self.scale.pack(pady=2)

    def set_scale(self, scale_factor):
        self.scale_factor = float(scale_factor)
        self.update_image_scale()

def main():
    root = tk.Tk()
    root.title("Binary Data Raster Viewer")
    app = RasterImageDisplay(root)
    root.mainloop()

if __name__ == "__main__":
    main()
