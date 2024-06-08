import cv2
import numpy as np

from utils import *

from typing import Any
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

class SilentLogger(trt.ILogger):
    def __init__(self):
       trt.ILogger.__init__(self)

    def log(self, severity, msg):
        pass 



class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()

class TrtModel:
    
    def __init__(self,engine_path,max_batch_size=1,dtype=np.float32):
        
        self.engine_path = engine_path
        self.dtype = dtype
        self.logger = SilentLogger()
        # self.logger = trt.Logger(trt.Logger.WARNING)

        self.runtime = trt.Runtime(self.logger)
        self.engine = self.load_engine(self.runtime, self.engine_path)
        self.max_batch_size = max_batch_size
        self.inputs, self.outputs, self.bindings, self.stream = self.allocate_buffers()
        self.context = self.engine.create_execution_context()

  
    @staticmethod
    def load_engine(trt_runtime, engine_path):
        trt.init_libnvinfer_plugins(None, "")             
        with open(engine_path, 'rb') as f:
            engine_data = f.read()
        engine = trt_runtime.deserialize_cuda_engine(engine_data)
        return engine
    
    def allocate_buffers(self):
        
        inputs = []
        outputs = []
        bindings = []
        shapes = []
        stream = cuda.Stream()
        
        for binding in self.engine:
            size = trt.volume(self.engine.get_binding_shape(binding)) * self.max_batch_size
            shapes.append(self.engine.get_binding_shape(binding))
            host_mem = cuda.pagelocked_empty(size, self.dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            
            bindings.append(int(device_mem))

            if self.engine.binding_is_input(binding):
                inputs.append(HostDeviceMem(host_mem, device_mem))
            else:
                outputs.append(HostDeviceMem(host_mem, device_mem))

        self.input_shape = shapes[0]
        self.output_shape = shapes[-1]

        
        return inputs, outputs, bindings, stream
       
            
    def __call__(self,x:np.ndarray,batch_size=1):
        
        x = x.astype(self.dtype)
        
        np.copyto(self.inputs[0].host,x.ravel())
        
        for inp in self.inputs:
            cuda.memcpy_htod_async(inp.device, inp.host, self.stream)
        
        self.context.execute_async(batch_size=batch_size, bindings=self.bindings, stream_handle=self.stream.handle)
        for out in self.outputs:
            cuda.memcpy_dtoh_async(out.host, out.device, self.stream) 
            
        self.stream.synchronize()
        return [out.host.reshape(batch_size,-1) for out in self.outputs]


class YOLOv10Trt:
    def __init__(self, 
                 weights_path: str, 
                 conf_threshold: float = 0.7, 
                 iou_threshold: float = 0.5,
                 batch_size: int = 1,
                 topk=10):
        
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.batch_size = batch_size
        self.topk = topk

        self.engine = TrtModel(weights_path)
        self.input_shape = self.engine.input_shape
        self.output_shape = self.engine.output_shape

        self.input_height, self.input_width = self.input_shape[-2:]

    def __call__(self, image: np.ndarray):
        return self.detect_objects(image)

    def detect_objects(self, image: np.ndarray):
        input_tensor, ratio = self.preprocess(image)

        outputs = self.engine(input_tensor, self.batch_size)[0] # for implicit 
        outputs = np.reshape(outputs, self.output_shape)

        self.boxes, self.scores, self.class_ids = self.postprocess(outputs, ratio)

        return self.boxes, self.scores, self.class_ids

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        self.img_height, self.img_width = image.shape[:2]

        input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_img, ratio = letterbox(
            input_img,
            new_shape=(self.input_width, self.input_height), 
            auto=False, 
            scaleFill=False, 
            scaleup=True, 
            stride=32
        )

        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)

        return input_tensor, ratio

    def postprocess(self, output: np.ndarray, ratio: tuple):
        predictions = output[0][:self.topk]

        scores = predictions[..., 4].astype(np.float32)
        class_ids = predictions[..., 5].astype(np.int32)
        boxes = predictions[..., :4].astype(np.float32)

        keep = scores > self.conf_threshold

        scores = scores[keep]
        class_ids = class_ids[keep]
        boxes = boxes[keep]

        # boxes = self.rescale_boxes(boxes, ratio)

        return boxes, scores, class_ids


    def rescale_boxes(self, boxes, ratio):
        wr, hr = ratio

        print(hr)

        if hr > 1:
            top_border = self.input_height / hr
        else:
            top_border = self.input_height * hr



        boxes[..., 1::2] -= top_border
        # input_shape = np.array([self.input_width, self.input_height, self.input_width, self.input_height])
        # boxes = np.divide(boxes, input_shape, dtype=np.float32)
        # boxes *= np.array([self.img_width, self.img_height, self.img_width, self.img_height])
        return boxes

    