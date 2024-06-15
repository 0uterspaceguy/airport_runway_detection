import flet as ft
import os

from utils import *
from .images_app import ImagesApp
from .videos_app import VideosApp
from .rtsp_app import RtspApp


class MainApp(ft.Column):
    def __init__(self, 
                    images_picker,
                    videos_picker,
                    upload_dir: str,
                    download_dir: str,
                    result_images_dir: str,
                    result_videos_dir: str,
                    result_txts_dir: str,
                    detector,
                    page,
                ):
        super().__init__()

        self.images_app = ImagesApp(images_picker=images_picker,
                                    upload_dir=upload_dir,
                                    download_dir=download_dir,
                                    result_images_dir=result_images_dir,
                                    result_txts_dir=result_txts_dir,
                                    detector=detector,)

        self.videos_app = VideosApp(videos_picker=videos_picker,
                                    upload_dir=upload_dir,
                                    download_dir=download_dir,
                                    result_videos_dir=result_videos_dir,
                                    page=page)
        self.rtsp_app = RtspApp()

        self.videos_app.visible = False
        self.rtsp_app.visible = False

        self.title = ft.Text("Демонстрация детектора", theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM)

        self.filter = ft.Tabs(
            tab_alignment="CENTER",
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="Images"), 
                  ft.Tab(text="Videos"), 
                  ft.Tab(text="RTSP")],
        )
        self.width = 1000

        self.controls = [
            ft.Row(
                controls=[
                    self.title,
                ],
                alignment="CENTER",

            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter,
                ],
            ),
            self.images_app,
            self.videos_app,
            self.rtsp_app,
        ]

    # def add_clicked(self, e):
    #     task = Task(self.new_task.value, self.task_status_change, self.task_delete)
    #     self.tasks.controls.append(task)
    #     self.new_task.value = ""
    #     self.update()

    # def task_status_change(self):
    #     self.update()

    # def task_delete(self, task):
    #     self.tasks.controls.remove(task)
    #     self.update()

    def before_update(self):
        current_status = self.filter.tabs[self.filter.selected_index].text

        if current_status == "Images":
            self.images_app.visible = True
            self.videos_app.visible = False
            self.rtsp_app.visible = False

        elif current_status == "Videos":
            self.images_app.visible = False
            self.videos_app.visible = True
            self.rtsp_app.visible = False
        
        elif current_status == "RTSP":
            self.images_app.visible = False
            self.videos_app.visible = False
            self.rtsp_app.visible = True
        

    def tabs_changed(self, e):
        self.update()
