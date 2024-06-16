in_video=$1
out_video=$2
result_path=$3

frame_w=1920
frame_h=1080
batch_size=1

muxer='mux.sink_0 nvstreammux name=mux batch-size=1 gpu-id=0 enable-padding=1 live-source=0 batched-push-timeout=40000 width=1920 height=1080'
primary='nvinfer batch-size=1 config-file-path=./models/primary/config.txt'
# tracker='nvtracker ll-lib-file=/opt/nvidia/deeepstream/deepstream-6.2/lib/libnvds_nvmultiobjecttracker.so tracker-width=640 tracker-height=384 ll-config-file=/workspace/custom_tracker.yml'
demuxer='nvstreamdemux name=demux demux.src_0'

gst-launch-1.0 -e filesrc location=${in_video} ! decodebin ! videoconvert ! nvvideoconvert ! ${muxer} ! ${primary} ! ${demuxer} ! dsexample full-frame=0 ! nvvideoconvert ! nvdsosd ! nvvideoconvert ! x264enc ! h264parse config-interval=1 ! mp4mux faststart=true ! filesink location=${out_video} 
mv /workspace/result_video.jsonl ${result_path}
