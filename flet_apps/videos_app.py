import flet as ft

from utils import *
import subprocess


class VideosApp(ft.Column):
    def __init__(self,
                videos_picker,
                upload_dir,
                result_videos_dir,
                ):
        super().__init__()

        self.upload_dir = upload_dir
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

        self.controls = [
            self.title_wrapper,

            ft.Row(
                controls=[self.load_button_wrapper,
                            self.load_pb_wrapper,
                            self.loaded_message_wrapper,],
                alignment = "LEFT",
                visible=True),

             ft.Row(
                controls=[self.infer_button_wrapper,
                            self.infer_pb_wrapper,
                            self.infer_message_wrapper,],
                alignment = "LEFT",
                visible=True),
                
                
            ]

    def infer_video(self, e):
        in_video = ""
        out_video = ""

        val = subprocess.check_call("./entrypoint_video.sh %s %s" % (in_video, out_video), shell=True)

    


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