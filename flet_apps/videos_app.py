from shutil import copyfile as cp
from utils import *
import subprocess
import jsonlines

import flet as ft
import numpy as np
import cv2

import zipfile
from natsort import natsorted
import base64
import time
import os


class VideosApp(ft.Column):
    def __init__(self,
                download_url,
                videos_picker,
                upload_dir,
                download_dir,
                result_videos_dir,
                page,
                ):
        super().__init__()
        self.page = page
        self.download_url = download_url

        self.upload_dir = upload_dir
        self.download_dir = download_dir
        self.result_videos_dir = result_videos_dir

        self.spacing = 30

        self.videos_picker = videos_picker
        self.videos_picker.on_upload = self.on_upload_video_progress
        self.videos_picker.on_result = self.upload_video

        self.prog_bars = {}

        self.title = ft.Text("Детекция на видео", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, text_align="CENTER")
        self.title_wrapper = ft.Row(
                controls=[self.title],
                alignment = "CENTER")

        self.load_pb = ft.ProgressBar(width=300, color="amber", bgcolor="#eeeeee") 
        self.load_pb_wrapper = ft.Column(
                controls=[self.load_pb],
                alignment = "CENTER",
                visible=False)

        self.load_button = ft.ElevatedButton("Выбрать видео...", on_click=lambda _: self.videos_picker.pick_files(allow_multiple=False))
        self.load_button_wrapper = ft.Column(
                controls=[self.load_button],
                alignment = "CENTER")

        self.loaded_message = ft.Text("", theme_style=ft.TextThemeStyle.BODY_LARGE, text_align="CENTER")
        self.loaded_message_wrapper = ft.Column(
                controls=[self.loaded_message],
                alignment = "CENTER",
                visible=False)

        self.infer_button = ft.ElevatedButton("Запустить инференс...", on_click=self.infer_video)
        self.infer_button_wrapper = ft.Column(
                controls=[self.infer_button],
                alignment = "CENTER",
                visible=False,)

        self.infer_pb = ft.ProgressBar(width=300, color="amber", bgcolor="#eeeeee") 
        self.infer_pb_wrapper = ft.Column(
                controls=[self.infer_pb],
                alignment = "CENTER",
                visible=False)

        self.infer_message = ft.Text("", theme_style=ft.TextThemeStyle.BODY_LARGE, text_align="CENTER")
        self.infer_message_wrapper = ft.Column(
                controls=[self.infer_message],
                alignment = "CENTER",
                visible=False)

        self.show_results_button = ft.ElevatedButton("Посмотреть отрисовку...", on_click=self.show_results)
        self.show_results_button_wrapper = ft.Column(
                controls=[self.show_results_button],
                alignment = "CENTER",
                visible=False,)
        
        self.download_results_button = ft.ElevatedButton("Скачать результаты...", on_click=self.download_results)
        self.download_results_button_wrapper = ft.Column(
                controls=[self.download_results_button],
                alignment = "CENTER",
                visible=False,)

        self.controls = [
            self.title_wrapper,
            ft.Row(
                controls=[self.load_button_wrapper,
                            self.load_pb_wrapper,
                            self.loaded_message_wrapper,],
                alignment = "CENTER",
                visible=True),
             ft.Row(
                controls=[self.infer_button_wrapper,
                            self.infer_pb_wrapper,
                            self.infer_message_wrapper,],
                alignment = "CENTER",
                visible=True),
            ft.Row(
                controls=[self.show_results_button_wrapper,
                          self.download_results_button_wrapper,],
                alignment = "CENTER",
                visible=True),
            ft.Column(
                controls=[],
                alignment = "CENTER",
                visible=False),
            ]

    # def slider_changed(self, e):
    #     timestamp = int(self.video.get_duration() * e.control.value)
    #     self.video.seek(timestamp)

    #     time.sleep(0.1)
    #     self.update()

    def make_timeline_image(self,):
        json_result_path = os.path.join(self.current_result_dir, "result_video.jsonl") 
        height, width = 40, 1000

        v = cv2.VideoCapture(self.out_video) 
        num_frames_orig = v.get(cv2.CAP_PROP_FRAME_COUNT) 

        if num_frames_orig < width:
            blank_image = np.ones((height, int(num_frames_orig)+1, 3)) * 114 
        else:
            blank_image = np.ones((height, width, 3)) * 114 
        
        frames_with_danger = []
        frames_with_no_danger = []

        with jsonlines.open(json_result_path) as reader:
            for detection in reader:
                class_id = detection["class_id"]
                frame_num = detection["frame_num"]

                if class_id2danger[int(class_id)]:
                    frames_with_danger.append(frame_num)
                else:
                    frames_with_no_danger.append(frame_num)

        if num_frames_orig < width:
            frames_with_danger = np.array(frames_with_danger).astype(np.int32)
            frames_with_no_danger = np.array(frames_with_no_danger).astype(np.int32)
        else:
            frames_with_danger = np.array(frames_with_danger) / num_frames_orig * width
            frames_with_danger = frames_with_danger.astype(np.int32)

            frames_with_no_danger = np.array(frames_with_no_danger) / num_frames_orig * width
            frames_with_no_danger = frames_with_no_danger.astype(np.int32)

        blank_image[:, frames_with_no_danger, 0] = 0
        blank_image[:, frames_with_no_danger, 1] = 255
        blank_image[:, frames_with_no_danger, 2] = 0
        
        blank_image[:, frames_with_danger, 0] = 0
        blank_image[:, frames_with_danger, 1] = 0
        blank_image[:, frames_with_danger, 2] = 255


        if num_frames_orig < width:
            blank_image = cv2.resize(blank_image, (width, height), interpolation=cv2.INTER_NEAREST)
        retval, buffer = cv2.imencode('.jpg', blank_image)
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        self.timeline_image = ft.Image(
                src_base64=jpg_as_text,
                width=width,
                height=height,
                fit=ft.ImageFit.CONTAIN,
        )

        self.timeline_image_wrapper = ft.Row(
                controls=[self.timeline_image],
                alignment = "CENTER",
                visible=True,)


    def download_results(self, e):
        sessions_list = natsorted(os.listdir(self.result_videos_dir))
        session_ts = sessions_list[-1]

        current_result_dir = os.path.join(self.result_videos_dir, session_ts)

        temp_zip_name = f"video_result_{session_ts}.zip"
        temp_zip_path = os.path.join(self.download_dir, temp_zip_name)

        file = zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED)
        for file_name in os.listdir(current_result_dir):
            file_path = os.path.join(current_result_dir, file_name)
            file.write(file_path, os.path.basename(file_path))
        file.close()

        e.page.launch_url(f"{self.download_url}/{temp_zip_name}", web_window_name='_self')


    def show_results(self, e):
        self.controls.pop(-1)

        out_video_name = os.path.basename(self.out_video)
        self.out_video_download_path = os.path.join(self.download_dir, out_video_name)

        cp(self.out_video, self.out_video_download_path)

        out_video_url = f"{self.download_url}/videos/{out_video_name}"
        video_media=ft.VideoMedia(resource=out_video_url)

        self.video = ft.Video(
            fit="FIT_WIDTH",
            expand=True,
            playlist=[video_media,],
            playlist_mode=ft.PlaylistMode.SINGLE,
            fill_color=ft.colors.BLACK,
            aspect_ratio=16/9,
            volume=0,
            autoplay=False,
            filter_quality=ft.FilterQuality.HIGH,
            muted=False,
            visible=True,
            on_loaded=lambda e: self.update(),
            on_error= lambda e: print(e.data, e.name, e.target)
        )

        video_wrapper = ft.Container(self.video)
        # video_slider = ft.Slider(min=0, max=1, on_change=self.slider_changed)

        self.controls.append(
                ft.Column(
                controls=[video_wrapper,
                        self.timeline_image_wrapper,
                        # video_slider,
                                ],
                visible=True))
        self.update()


    def infer_video(self, e):
        self.infer_pb_wrapper.visible = True
        self.infer_button.disabled = True
        self.download_results_button.disabled = True
        self.show_results_button.disabled = True
        self.load_button.disabled = True

        self.infer_message_wrapper.visible = False

        self.update()

        self.session_ts = make_timestamp()
        self.current_result_dir = os.path.join(self.result_videos_dir, self.session_ts)

        mkdir(self.current_result_dir)

        video_name = os.listdir(self.upload_dir)[0]
        self.in_video = os.path.join(self.upload_dir, video_name)
        self.out_video = os.path.join(self.current_result_dir, video_name)

        start_time = time.time()
        val = subprocess.check_call("./entrypoint_video.sh %s %s %s" % (self.in_video, self.out_video, self.current_result_dir), shell=True)
        end_time = time.time()

        self.infer_pb_wrapper.visible = False

        self.infer_message.value =  f"Время обработки: {round(end_time - start_time, 2)} секунд."
        self.infer_message_wrapper.visible = True
        self.show_results_button_wrapper.visible = True
        self.download_results_button_wrapper.visible = True
        self.infer_button.disabled = False
        self.download_results_button.disabled = False
        self.show_results_button.disabled = False
        self.load_button.disabled = False

        self.make_timeline_image()
        self.update()


    def upload_video(self, e):
        if self.videos_picker.result != None and self.videos_picker.result.files != None:
            self.download_results_button.disabled = True
            self.show_results_button.disabled = True
            self.infer_button.disabled = True
            self.loaded_message_wrapper.visible = False
            self.load_pb.value = 0
            self.load_pb_wrapper.visible = True
            self.update()

            reinit_dir(self.upload_dir)
            upload_list = []

            for f in self.videos_picker.result.files:
                upload_list.append(
                   ft.FilePickerUploadFile(
                    f.name,
                    upload_url=e.page.get_upload_url(f.name, 600))
                )
            self.load_button.disabled = True
            self.videos_picker.upload(upload_list)  

    def on_upload_video_progress(self, e):
        current_progress = e.progress

        self.load_pb.value = current_progress

        if current_progress == 1:
            self.download_results_button.disabled = False
            self.show_results_button.disabled = False
            self.infer_button.disabled = False

            self.load_pb_wrapper.visible = False
            self.load_button.disabled = False

            self.loaded_message.value = f"Загружено видео: {e.file_name}"
            self.loaded_message_wrapper.visible = True
            self.infer_button_wrapper.visible = True
        
        self.update()