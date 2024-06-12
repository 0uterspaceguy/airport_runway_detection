FROM nvcr.io/nvidia/deepstream:6.2-devel
ARG DEBIAN_FRONTEND=noninteractive
ARG CUDA_VER=11

RUN apt-get update && apt-get install python3-dev python3-pip ffmpeg libsm6 libxext6 -y

#Just for inference on files
COPY requirements_torch.txt /workspace/
RUN pip3 install -r /workspace/requirements_torch.txt
RUN git clone https://github.com/THU-MIG/yolov10.git && pip3 install -e yolov10/
RUN git clone https://github.com/nlohmann/json.git

COPY . /workspace/

#Install custom libs
WORKDIR /workspace/plugins/gst_custombboxparser/
RUN make && make install

WORKDIR /workspace/plugins/gst_detdumper
RUN make && make install 

# sudo apt install libmpv-dev mpv

WORKDIR /workspace
# CMD /usr/src/tensorrt/bin/trtexec --onnx=/workspace/models/primary/model.onnx --saveEngine=/workspace/models/primary/model.onnx_b1_gpu0_fp16.engine --fp16





