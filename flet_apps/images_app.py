import zipfile
import flet as ft

from utils import * 
from random import shuffle, choice

import cv2
import base64

class ImagesApp(ft.Column):
    def __init__(self, 
                images_picker,
                upload_dir,
                download_dir,
                result_images_dir,
                result_txts_dir,
                detector,):
        super().__init__()

        self.detector = detector
        self.upload_dir = upload_dir
        self.download_dir = download_dir
        self.result_images_dir = result_images_dir
        self.result_txts_dir = result_txts_dir

        # self.alignment = "CENTER"
        self.spacing = 30

        self.images_picker = images_picker
        self.images_picker.on_upload = self.on_upload_images_progress
        self.images_picker.on_result = self.upload_images

        self.files_to_load = 0
        self.prog_bars = {}

        self.title = ft.Text("Детекция на изображениях", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, text_align="CENTER")
        self.title_wrapper = ft.Row(
                controls=[self.title],
                alignment = "CENTER"
                )
        # self.description = ft.Text("В этой вкладке вы можете загрузить одно или несколько изображений и запустить инференс.", 
        #                             theme_style=ft.TextThemeStyle.BODY_LARGE, text_align="CENTER")

        self.load_pb = ft.ProgressBar(width=300, color="amber", bgcolor="#eeeeee") 
        self.load_pb_wrapper = ft.Column(
                controls=[self.load_pb],
                alignment = "CENTER",
                visible=False)

        self.load_button = ft.ElevatedButton("Выбрать изображения...", on_click=lambda _: self.images_picker.pick_files(allow_multiple=True))
        self.load_button_wrapper = ft.Column(
                controls=[self.load_button],
                alignment = "CENTER"
                )

        self.loaded_message = ft.Text("", theme_style=ft.TextThemeStyle.BODY_LARGE, text_align="CENTER")
        self.loaded_message_wrapper = ft.Column(
                controls=[self.loaded_message],
                alignment = "CENTER",
                visible=False)

        
        self.infer_button = ft.ElevatedButton("Запустить инференс...", on_click=lambda _: self.detector.infer_dir(self.upload_dir, self.result_txts_dir, self.result_images_dir))
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

        self.download_button = ft.ElevatedButton("Скачать результаты...", on_click=self.download_results)
        self.download_button_wrapper = ft.Column(
                controls=[self.download_button],
                alignment = "CENTER",
                visible=False,)

        self.show_results_button = ft.ElevatedButton("Посмотреть отрисовку...", on_click=self.show_results)
        self.show_results_button_wrapper = ft.Column(
                controls=[self.show_results_button],
                alignment = "CENTER",
                visible=False,)

        self.image = ft.Image(
            src=f"no path",
                width=500,
                height=500,
                fit=ft.ImageFit.CONTAIN,
        )

        self.image_wrapper = ft.Column(
                controls=[self.image],
                alignment = "CENTER",
                visible=False,)

        self.left_button = ft.IconButton(
                    icon=ft.icons.REMOVE,
                    icon_color="white600",
                    icon_size=40,
                    on_click=self.left_click
                )

        self.left_button_wrapper = ft.Column(
                controls=[self.left_button],
                alignment = "LEFT",
                visible=False,)

        self.right_button = ft.IconButton(
                    icon=ft.icons.ADD,
                    icon_color="white600",
                    icon_size=40,
                    on_click=self.right_click
                )

        self.right_button_wrapper = ft.Column(
                controls=[self.right_button],
                alignment = "RIGHT",
                visible=False,)

        

        self.detector.pbar = self.infer_pb
        self.detector.pbar_w = self.infer_pb_wrapper
        self.detector.msg = self.infer_message
        self.detector.msg_w = self.infer_message_wrapper

        self.detector.app_page = self

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

            ft.Row(
                controls=[self.download_button_wrapper,
                            self.show_results_button_wrapper],
                alignment = "CENTER",
                visible=True),

            ft.Row(
                controls=[self.left_button_wrapper, self.image_wrapper, self.right_button_wrapper],
                alignment = "CENTER",
                visible=True)

            # self.load_button_wrapper,
            # self.load_pb_wrapper,
            # self.loaded_message_wrapper,

            # self.infer_button_wrapper,
            # self.infer_pb_wrapper,
            # self.infer_message_wrapper,
            ]

    def download_results(self, e):
        temp_zip_name = "yolo_results.zip"
        temp_zip_path = os.path.join(self.download_dir, temp_zip_name)

        file = zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED)
        for file_name in os.listdir(self.result_txts_dir):
            file_path = os.path.join(self.result_txts_dir, file_name)
            file.write(file_path)
        file.close()

        e.page.launch_url(f"http://127.0.0.1:57777/download/{temp_zip_name}", web_window_name='_self')

    def right_click(self, e):
        self.current_image_idx = self.current_image_idx + 1 if self.current_image_idx < len(self.drawed_images)-1 else self.current_image_idx
        self.set_image(self.current_image_idx)

    def left_click(self, e):
        self.current_image_idx = self.current_image_idx - 1 if self.current_image_idx > 0 else self.current_image_idx
        self.set_image(self.current_image_idx)

    def set_image(self, idx):
        image = cv2.imread(self.drawed_images[idx])

        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

        self.image.src_base64 = jpg_as_text

        self.image.update()
        self.update()


    def show_results(self, e):
        self.drawed_images = [os.path.join(self.result_images_dir, image_name) for image_name in os.listdir(self.result_images_dir)]
        shuffle(self.drawed_images)

        self.image_wrapper.visible = True

        self.left_button_wrapper.visible = True
        self.right_button_wrapper.visible = True

        self.current_image_idx = 0
        self.set_image(self.current_image_idx)



    def upload_images(self, e):
        if self.images_picker.result != None and self.images_picker.result.files != None:

            reinit_dir(self.upload_dir)

            upload_list = []
            self.prog_bars = {}
            self.num_files_to_load = 0

            self.loaded_message_wrapper.visible = False

            self.load_pb.value = 0
            self.load_pb_wrapper.visible = True

            self.update()

            for f in self.images_picker.result.files:
                upload_list.append(
                   ft.FilePickerUploadFile(
                    f.name,
                    upload_url=e.page.get_upload_url(f.name, 600))
                )

            self.num_files_to_load = len(upload_list)
            self.load_button.disabled = True
            self.images_picker.upload(upload_list)  

    def on_upload_images_progress(self, e):
        self.prog_bars[e.file_name] = e.progress
        current_progress = sum([value == 1 for value in self.prog_bars.values()]) / self.num_files_to_load

        self.load_pb.value = current_progress
        if current_progress == 1:
            self.load_pb_wrapper.visible = False
            self.load_button.disabled = False

            self.loaded_message.value = f"Изображений загружено: {self.num_files_to_load}"
            self.loaded_message_wrapper.visible = True
            self.infer_button_wrapper.visible = True
        
        self.update()