import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
import webbrowser
import time

import cv2 as cv
import mediapipe as mp
import json

import cursor_movement_2

class SetupWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Active Eye Setup")
        self.master.attributes('-fullscreen', True)

        self.positions = ['topleft', 'topcenter', 'topright', 'midleft', 'midcenter', 'midright', 'bottomleft', 'bottomcenter', 'bottomright']
        self.current_position_index = 0

        self.cap = cv.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.iris_positions = {}
        self.eye_vertical_distance = {}

        self.show_instructions()

    def show_instructions(self):
        instruction_window = tk.Toplevel(self.master)
        instruction_window.title("Instructions")
        instruction_window.attributes('-topmost', True)  # Keep on top

        message_label = ttk.Label(instruction_window, text="Setting things up!!!\n\nIn a moment, you will see highlighted circles at different positions on the screen, one by one. You need to look at the center of the circle as it shows up.", font=('Helvetica', 18), justify='center')
        message_label.pack(padx=50, pady=50)

        start_button = ttk.Button(instruction_window, text="Start", command=lambda: [instruction_window.destroy(), self.setup_window()])
        start_button.pack(pady=20)

    def setup_window(self):
        self.setup_label = ttk.Label(self.master, text="Setup Initialization", font=('Helvetica', 24, 'bold'))
        self.setup_label.pack(pady=50)

        self.canvas = tk.Canvas(self.master, bg="white", highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.highlight_next_position()

    def highlight_next_position(self):
        if self.current_position_index < len(self.positions):
            position = self.positions[self.current_position_index]
            self.draw_highlight_area(position)
            self.current_position_index += 1
        else:
            self.complete_setup()

    def draw_highlight_area(self, position):
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()

        radius = 50
        x, y = self.get_position_coordinates(position, width, height)
        self.animate_circle(x, y, radius, position)

    def get_position_coordinates(self, position, width, height):
        if position == 'topleft':
            return 0, 0
        elif position == 'topcenter':
            return width // 2, 0
        elif position == 'topright':
            return width, 0
        elif position == 'midleft':
            return 0, height // 2
        elif position == 'midcenter':
            return width // 2, height // 2
        elif position == 'midright':
            return width, height // 2
        elif position == 'bottomleft':
            return 0, height
        elif position == 'bottomcenter':
            return width // 2, height
        elif position == 'bottomright':
            return width, height

    def animate_circle(self, x, y, radius, position):
        circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="red", width=5)
        self.process_and_read_coordinates(position)
        self.master.after(1400, lambda: self.canvas.delete(circle))
        self.master.after(1400, self.highlight_next_position)

    def process_and_read_coordinates(self, position):
        _, frame = self.cap.read()
        frame = cv.flip(frame, 1)

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # Processing through face mesh
        output = self.face_mesh.process(rgb_frame)
        face_landmarks = output.multi_face_landmarks

        # Frame height and width to get necessary scaling
        frame_h, frame_w, _ = frame.shape

        if face_landmarks:
            landmarks = face_landmarks[0].landmark
            right_eye_iris_center = landmarks[473]
            pos_x = right_eye_iris_center.x * frame_w
            pos_y = right_eye_iris_center.y * frame_h
            self.iris_positions[position] = (pos_x, pos_y)
            cv.circle(frame, (int(pos_x), int(pos_y)), 1, (0, 255, 0), -1)
            path = "imgs/" + position + ".png"
            cv.imwrite(path, frame)

            upper_lid = landmarks[386] # Top of the right eye
            lower_lid = landmarks[374] # Bottom of the right eye

            upper_y = int(upper_lid.y * frame_h)
            lower_y = int(lower_lid.y * frame_h)

            vertical_distance = lower_y - upper_y
            self.eye_vertical_distance[position] = vertical_distance


    def complete_setup(self):
        with open('iris_calibrations.json', 'w') as f:
            json.dump(self.iris_positions, f)

        with open('eye_vertical_dist.json', 'w') as f:
            json.dump(self.eye_vertical_distance, f)
        
        self.canvas.destroy()
        self.setup_label.config(text="Redirecting you to the browser", font=('Helvetica', 24, 'bold'))
        self.master.after(2000, self.open_browser)

    def open_browser(self):
        url = "https://example.com"  # Replace this with your specific URL
        webbrowser.open(url)
        self.master.destroy()

def start_setup():
    root = tk.Tk()
    setup_window = SetupWindow(root)
    root.mainloop()

if __name__ == "__main__":
    start_setup()
    cursor_movement_2.main()