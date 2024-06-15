from ultralytics import YOLOv10
from utils import *

import time
from tqdm import tqdm

import os

class Detector():
    def __init__(self,
                weights_path: str="",
                iou_thres: float=0.5,
                conf_thres: float=0.3,
                imgsz: int=1024,):

        self.model = YOLOv10(weights_path)
        self.iou_thres = iou_thres
        self.conf_thres = conf_thres
        self.imgsz = imgsz

        self.app_page = None


    def infer_dir(self,
                  images_dir: str,
                  result_txts_dir: str,
                  result_images_dir: str):
        
        session_ts = make_timestamp()
        
        current_results_txts_dir = os.path.join(result_txts_dir, session_ts)
        current_result_images_dir = os.path.join(result_images_dir, session_ts)

        reinit_dir(current_results_txts_dir)
        reinit_dir(current_result_images_dir)

        self.app_page.infer_pb_wrapper.visible=True
        self.app_page.infer_pb.value = 0
        self.app_page.infer_message_wrapper.visible = False
        self.app_page.update()

        results = self.model(images_dir, 
                    imgsz=self.imgsz, 
                    conf=self.conf_thres,
                    iou=self.iou_thres,
                    max_det=10,
                    save_txt=True,
                    stream=True,
                    verbose=False) 

        total_num = len(os.listdir(images_dir))

        start_time = time.time()

        for idx, result in tqdm(enumerate(results, start=1), total=total_num, desc="Inference"):
            image_name = os.path.basename(result.path)

            label_name = os.path.splitext(image_name)[0]+".txt"
            label_path = os.path.join(current_results_txts_dir, label_name)
            result.save_txt(label_path)

            self.pbar.value = idx/total_num
            self.app_page.update()

            result.save(os.path.join(current_result_images_dir, image_name))

        end_time = time.time()

        self.app_page.infer_pb_wrapper.visible=False
        self.app_page.infer_message.value = f"Обработано изображений: {total_num}. \n Время обработки: {round(end_time - start_time, 2)} секунд. \n"
        self.app_page.infer_message_wrapper.visible = True

        self.app_page.show_results_button_wrapper.visible = True
        self.app_page.download_txts_button_wrapper.visible = True
        self.app_page.download_images_button_wrapper.visible = True


        self.app_page.update()
        rmdir(result.save_dir)