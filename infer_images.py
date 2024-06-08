import os
import cv2
import argparse
from tqdm import tqdm

from ultralytics import YOLOv10
from utils import mkdir, rmdir


def parse_args():
    parser = argparse.ArgumentParser(description='Make predictions on images')
    parser.add_argument('--input', type=str, default='./images', help='path to images')
    parser.add_argument('--output', type=str, default='./images_results', help='path to result files')
    parser.add_argument('--model', type=str, default='./models/primary/model.pt', help='path to model engine')
    parser.add_argument('--imgsz', type=int, default=1024, help='size of image')
    parser.add_argument('--iou_thres', type=float, default=0.9, help='iou threshold')
    parser.add_argument('--conf_thres', type=float, default=0.2, help='confidence threshold')


    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    rmdir(args.output)
    mkdir(args.output)

    model = YOLOv10(args.model)

    results = model(args.input, 
                    imgsz=args.imgsz, 
                    conf=args.conf_thres,
                    iou=args.iou_thres,
                    max_det=10,
                    save_txt=True,
                    stream=True,
                    verbose=False) 

    for result in tqdm(results, total=len(os.listdir(args.input)), desc="Inference"):
        
        image_name = os.path.basename(result.path)

        label_name = os.path.splitext(image_name)[0]+".txt"
        label_path = os.path.join(args.output, label_name)
        result.save_txt(label_path)

        # result.save(f"drawed/{image_name}")

    rmdir(result.save_dir)


    

        









































    exit()

    for idx, image_name in enumerate(tqdm(os.listdir(args.input))):
        image_path = os.path.join(args.input, image_name)

        label_name = os.path.splitext(image_name)[0]+".txt"
        label_path = os.path.join(args.output, label_name)

        image_bgr = cv2.imread(image_path)
        image_h, image_w = image_bgr.shape[:-1]



        model.predict()

        boxes, scores, class_ids = model(image_bgr)

        for box, score, class_id in zip(boxes, scores, class_ids):
            x1, y1, x2, y2 = box
            box_w, box_h = x2-x1, y2-y1

            xn = (x2-box_w/2)/image_w
            yn = (y2-box_h/2)/image_h
            wn = box_w/image_w
            hn = box_h/image_h

            line = f"{class_id} {xn} {yn} {wn} {hn}\n"

            with open(label_path, "a", encoding="utf-8") as result_file:
                result_file.write(line)

            image_bgr = cv2.rectangle(image_bgr, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 3) 
        cv2.imwrite(f"drawed/{idx}.png", image_bgr)


