from contextlib import asynccontextmanager

import flet as ft
import flet.fastapi as flet_fastapi
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import yaml
import uvicorn

import yaml
import os

from utils import *
from flet_apps import MainApp, Detector
from downloader import range_requests_response

with open("/workspace/flet_app_config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()

app = FastAPI(lifespan=lifespan)



@app.get(path="/download/videos/{filename}")
def get_video(request: Request, filename: str):
    file_path = os.path.join(config["downloads_dir"], filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return range_requests_response(
        request, file_path=file_path, content_type="video/mp4"
    )

@app.get(path="/download/{filename}")
def get_video(request: Request, filename: str):
    file_path = os.path.join(config["downloads_dir"], filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    response = FileResponse(path=file_path, filename=filename)
    return response


def main(page: ft.Page,):
    uploads_dir = config["uploads_dir"]
    downloads_dir = config["downloads_dir"]
    results_dir = config["results_dir"]

    mkdir(uploads_dir)
    mkdir(downloads_dir)
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

    page.title = config["title"]
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "ALWAYS"

    page.overlay.append(images_picker)
    page.overlay.append(videos_picker)
    page.update()

    download_url = config['download_server_url']

    app_flet = MainApp(download_url=download_url,
                    images_picker=images_picker,
                    videos_picker=videos_picker,
                    upload_dir=uploads_dir,
                    download_dir=downloads_dir,
                    result_images_dir=result_images_dir,
                    result_videos_dir=result_videos_dir,
                    result_txts_dir=result_txts_dir,
                    detector=detector,
                    page=page)

    page.add(app_flet)

app.mount("/detector", flet_fastapi.app(main, upload_dir="./uploads"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=57777, log_level="info")
