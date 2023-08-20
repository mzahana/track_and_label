import cv2
import os
import tkinter as tk
from tkinter import filedialog, Scale, Entry, Label, Button, Frame
from PIL import Image, ImageTk
import threading

class VideoPlayer:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = None
        self.vid = None

        self.canvas_frame = Frame(window)
        self.canvas_frame.grid(row=0, column=1, rowspan=8)

        self.canvas = tk.Canvas(self.canvas_frame, width=320, height=240)
        self.canvas.grid(row=0, column=0)

        self.canvas_end = tk.Canvas(self.canvas_frame, width=320, height=240)
        self.canvas_end.grid(row=0, column=1)

        self.canvas_play = tk.Canvas(self.canvas_frame, width=640, height=240)
        self.canvas_play.grid(row=1, column=0, columnspan=2)

        self.btn_select_video = Button(window, text="Select Video", width=15, command=self.select_video)
        self.btn_select_video.grid(row=0, column=0, sticky=tk.W+tk.E)

        self.label_video_path = Label(window, text="Video Path: None")
        self.label_video_path.grid(row=1, column=0, sticky=tk.W)

        self.btn_select_output = Button(window, text="Select Output", width=15, command=self.select_output)
        self.btn_select_output.grid(row=2, column=0, sticky=tk.W+tk.E)

        self.label_output_path = Label(window, text="Output Path: None")
        self.label_output_path.grid(row=3, column=0, sticky=tk.W)

        self.scale_start = Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, label="Start Time (s)", command=self.update_start_frame)
        self.scale_start.grid(row=4, column=0, sticky=tk.W+tk.E)

        self.scale_end = Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, label="End Time (s)", command=self.update_end_frame)
        self.scale_end.grid(row=5, column=0, sticky=tk.W+tk.E)

        self.label_prefix = Label(window, text="Prefix:")
        self.label_prefix.grid(row=6, column=0, sticky=tk.W)

        self.entry_prefix = Entry(window)
        self.entry_prefix.grid(row=7, column=0, sticky=tk.W+tk.E)

        self.label_fps = Label(window, text="FPS:")
        self.label_fps.grid(row=8, column=0, sticky=tk.W)

        self.entry_fps = Entry(window)
        self.entry_fps.grid(row=9, column=0, sticky=tk.W+tk.E)
        self.entry_fps.insert(0, "10")

        self.btn_extract = Button(window, text="Extract Frames", width=15, command=self.start_extraction)
        self.btn_extract.grid(row=10, column=0, sticky=tk.W+tk.E)

        self.btn_play = Button(self.canvas_frame, text="Play", width=15, command=self.play_video)
        self.btn_play.grid(row=2, column=0, columnspan=2)

        self.label_status = Label(window, text="Status: Ready")
        self.label_status.grid(row=11, column=0, sticky=tk.W)

        self.playing = False

        self.window.mainloop()

    def select_video(self):
        self.video_source = filedialog.askopenfilename()
        self.label_video_path.config(text=f"Video Path: {self.video_source}")
        self.vid = cv2.VideoCapture(self.video_source)
        self.scale_start.config(to=int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT)/self.vid.get(cv2.CAP_PROP_FPS)))
        self.scale_end.config(to=int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT)/self.vid.get(cv2.CAP_PROP_FPS)))

    def select_output(self):
        self.output_dir = filedialog.askdirectory()
        self.label_output_path.config(text=f"Output Path: {self.output_dir}")

    def update_start_frame(self, value):
        if not self.vid:
            return
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, int(float(value) * self.vid.get(cv2.CAP_PROP_FPS)))
        ret, frame = self.vid.read()
        if not ret:
            return
        frame = cv2.resize(frame, (320, 240))
        self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.photo))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def update_end_frame(self, value):
        if not self.vid:
            return
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, int(float(value) * self.vid.get(cv2.CAP_PROP_FPS)))
        ret, frame = self.vid.read()
        if not ret:
            return
        frame = cv2.resize(frame, (320, 240))
        self.photo_end = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.photo_end = ImageTk.PhotoImage(image=Image.fromarray(self.photo_end))
        self.canvas_end.create_image(0, 0, image=self.photo_end, anchor=tk.NW)

    def play_video(self):
        if not self.vid:
            return
        if not self.playing:
            self.playing = True
            self.btn_play.config(text="Pause")
            start_frame = int(self.scale_start.get() * self.vid.get(cv2.CAP_PROP_FPS))
            end_frame = int(self.scale_end.get() * self.vid.get(cv2.CAP_PROP_FPS))
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            while self.vid.get(cv2.CAP_PROP_POS_FRAMES) < end_frame and self.playing:
                ret, frame = self.vid.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (640, 240))
                self.photo_play = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo_play = ImageTk.PhotoImage(image=Image.fromarray(self.photo_play))
                self.canvas_play.create_image(0, 0, image=self.photo_play, anchor=tk.NW)
                self.window.update()
            self.playing = False
            self.btn_play.config(text="Play")
        else:
            self.playing = False
            self.btn_play.config(text="Play")

    def start_extraction(self):
        self.label_status.config(text="Status: Extraction in progress")
        self.disable_widgets()
        threading.Thread(target=self.extract_frames).start()

    def extract_frames(self):
        if not self.vid or not self.output_dir:
            return
        prefix = self.entry_prefix.get()
        start_time = self.scale_start.get()
        end_time = self.scale_end.get()
        extraction_fps = int(self.entry_fps.get())

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            for file_name in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

        video_fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        start_frame = int(start_time * video_fps)
        end_frame = int(end_time * video_fps)
        frame_step = int(video_fps / extraction_fps)

        for i in range(start_frame, end_frame, frame_step):
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = self.vid.read()
            if not ret:
                print(f"Error: Could not read frame {i}")
                continue

            image_path = os.path.join(self.output_dir, f"{prefix}_{i}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Saved frame {i} to {image_path}")

        self.label_status.config(text="Status: Extraction is Done")
        self.enable_widgets()

    def disable_widgets(self):
        self.scale_start.config(state=tk.DISABLED)
        self.scale_end.config(state=tk.DISABLED)
        self.entry_prefix.config(state=tk.DISABLED)
        self.btn_extract.config(state=tk.DISABLED)
        self.btn_play.config(state=tk.DISABLED)
        self.btn_select_video.config(state=tk.DISABLED)
        self.btn_select_output.config(state=tk.DISABLED)

    def enable_widgets(self):
        self.scale_start.config(state=tk.NORMAL)
        self.scale_end.config(state=tk.NORMAL)
        self.entry_prefix.config(state=tk.NORMAL)
        self.btn_extract.config(state=tk.NORMAL)
        self.btn_play.config(state=tk.NORMAL)
        self.btn_select_video.config(state=tk.NORMAL)
        self.btn_select_output.config(state=tk.NORMAL)

    def __del__(self):
        if self.vid and self.vid.isOpened():
            self.vid.release()

root = tk.Tk()
VideoPlayer(root, "Video Player")