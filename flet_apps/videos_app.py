import flet as ft

from utils import *
import subprocess

import time
import os

from shutil import copyfile as cp


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

        # self.alignment = "CENTER"
        self.spacing = 30

        self.videos_picker = videos_picker
        self.videos_picker.on_upload = self.on_upload_video_progress
        self.videos_picker.on_result = self.upload_video

        self.prog_bars = {}

        self.title = ft.Text("Детекция на видео", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, text_align="CENTER")
        self.title_wrapper = ft.Row(
                controls=[self.title],
                alignment = "CENTER"
                )


        self.load_pb = ft.ProgressBar(width=300, color="amber", bgcolor="#eeeeee") 
        self.load_pb_wrapper = ft.Column(
                controls=[self.load_pb],
                alignment = "CENTER",
                visible=False)

        self.load_button = ft.ElevatedButton("Выбрать видео...", on_click=lambda _: self.videos_picker.pick_files(allow_multiple=False))
        self.load_button_wrapper = ft.Column(
                controls=[self.load_button],
                alignment = "CENTER"
                )

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
                controls=[self.show_results_button_wrapper],
                alignment = "CENTER",
                visible=True),

            ft.Column(
                controls=[],
                alignment = "CENTER",
                visible=False),
                
                
            ]

    def slider_changed(self, e):
        timestamp = int(self.video.get_duration() * e.control.value)
        self.video.seek(timestamp)

        time.sleep(0.1)
        self.update()

    def show_results(self, e):
        self.controls.pop(-1)

        out_video_name = os.path.basename(self.out_video)
        self.out_video_download_path = os.path.join(self.download_dir, out_video_name)

        cp(self.out_video, self.out_video_download_path)

        out_video_url = f"{self.download_url}/videos/{out_video_name}"
        print(out_video_url)


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
        video_slider = ft.Slider(min=0, max=1, on_change_end=self.slider_changed)

        self.controls.append(
                ft.Column(
                controls=[video_wrapper,
                        video_slider,
                                ],
                alignment = "CENTER",
                visible=True),
        )

        self.update()


    def infer_video(self, e):
        self.infer_pb_wrapper.visible = True
        self.infer_button.disabled = True
        self.infer_message_wrapper.visible = False

        self.update()

        video_name = os.listdir(self.upload_dir)[0]
        self.in_video = os.path.join(self.upload_dir, video_name)
        self.out_video = os.path.join(self.result_videos_dir, video_name)

        start_time = time.time()

        val = subprocess.check_call("./entrypoint_video.sh %s %s" % (self.in_video, self.out_video), shell=True)

        end_time = time.time()

        self.infer_pb_wrapper.visible = False

        self.infer_message.value =  f"Время обработки: {round(end_time - start_time, 2)} секунд."
        self.infer_message_wrapper.visible = True
        self.show_results_button_wrapper.visible = True
        self.infer_button.disabled = False

        self.update()



    def upload_video(self, e):
        if self.videos_picker.result != None and self.videos_picker.result.files != None:

            reinit_dir(self.upload_dir)

            upload_list = []

            self.loaded_message_wrapper.visible = False
            self.load_pb.value = 0
            self.load_pb_wrapper.visible = True
            self.update()

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
            self.load_pb_wrapper.visible = False
            self.load_button.disabled = False

            self.loaded_message.value = f"Загружено видео: {e.file_name}"
            self.loaded_message_wrapper.visible = True
            self.infer_button_wrapper.visible = True
        
        self.update()