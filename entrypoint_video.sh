
in_video=videos/video0.mp4

muxer='mux.sink_0 nvstreammux name=mux batch-size=1 enable-padding=1 live-source=0 batched-push-timeout=40000 width=1920 height=1080'
primary='nvinfer batch-size=1 config-file-path=./models/primary/config.txt'
tracker='nvtracker ll-lib-file=/opt/nvidia/deepstream/deepstream-6.2/lib/libnvds_nvmultiobjecttracker.so tracker-width=640 tracker-height=384 ll-config-file=/workspace/custom_tracker.yml'
demuxer='nvstreamdemux name=demux demux.src_0'
out_video=drawed_videos/video0.mkv

rm ./result_video.jsonl
# gst-launch-1.0 filesrc location=${in_video} ! decodebin ! queue ! ${muxer} ! queue ! ${primary} ! queue ! ${demuxer} ! queue ! nvvideoconvert ! nvdsosd ! nvvideoconvert ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)I420" ! nvv4l2h265enc ! h265parse ! matroskamux ! queue ! filesink location=${out_video}
gst-launch-1.0 filesrc location=${in_video} ! decodebin ! ${muxer} ! ${primary} ! ${tracker} ! ${demuxer} ! nvvideoconvert ! dsexample full-frame=0 ! nvdsosd ! nvvideoconvert ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)I420" ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=${out_video}


