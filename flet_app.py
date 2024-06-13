import yaml
import os

import flet as ft

from utils import *
from flet_apps import MainApp, Detector

def main(page: ft.Page,
        config_path: str = "./flet_app_config.yaml"):

    with open(config_path) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    page.title = config["title"]
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    upload_dir = config["uploads_dir"]
    results_dir = config["results_dir"]

    mkdir(upload_dir)
    mkdir(results_dir)

    result_images_dir = os.path.join(results_dir, "images")
    result_videos_dir = os.path.join(results_dir, "videos")
    result_txts_dir = os.path.join(results_dir, "txts")

    mkdir(result_images_dir)
    mkdir(result_videos_dir)
    mkdir(result_txts_dir)

    detector = Detector(**config["Detector"])      

    images_picker = ft.FilePicker()
    videos_picker = ft.FilePicker()

    page.overlay.append(images_picker)
    page.overlay.append(videos_picker)
    page.update()

    page.scroll = "ALWAYS"

    app = MainApp(images_picker=images_picker,
                    videos_picker=videos_picker,
                    upload_dir=upload_dir,
                    result_images_dir=result_images_dir,
                    result_videos_dir=result_videos_dir,
                    result_txts_dir=result_txts_dir,
                    detector=detector)

    page.add(app)


if __name__ == "__main__":
    ft.app(target=main, upload_dir="./uploads", view=ft.AppView.WEB_BROWSER)
