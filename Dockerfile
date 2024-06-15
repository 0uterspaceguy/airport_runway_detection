FROM nvcr.io/nvidia/deepstream:6.2-devel
ARG DEBIAN_FRONTEND=noninteractive
ARG CUDA_VER=11

RUN echo pwd

RUN apt-get update && apt-get install python3-dev python3-pip ffmpeg libsm6 libxext6 zenity libmpv-dev mpv -y

#Just for inference on files
COPY requirements.txt /workspace/
RUN pip3 install -r /workspace/requirements.txt
RUN git clone https://github.com/THU-MIG/yolov10.git && pip3 install -e yolov10/
RUN git clone https://github.com/nlohmann/json.git

COPY . /workspace/

#Install custom libs
WORKDIR /workspace/plugins/gst_custombboxparser/
RUN make && make install

WORKDIR /workspace/plugins/gst_detdumper
RUN make && make install 

RUN apt-get install --reinstall gstreamer1.0-plugins-ugly gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-libav gstreamer1.0-plugins-bad gstreamer1.0-plugins-good libavcodec58 libavutil56 libvpx6 libx264-155 libx265-179 libmpg123-0 -y


WORKDIR /workspace


# CMD /usr/src/tensorrt/bin/trtexec --onnx=/workspace/models/primary/model.onnx --saveEngine=/workspace/models/primary/model.onnx_b1_gpu0_fp16.engine --fp16


