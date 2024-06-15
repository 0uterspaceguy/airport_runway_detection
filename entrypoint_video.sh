# in_video=videos/video0.mp4
in_video=$1
echo $in_video

muxer='mux.sink_0 nvstreammux name=mux batch-size=1 enable-padding=1 live-source=0 batched-push-timeout=40000 width=1920 height=1080'
primary='nvinfer batch-size=1 config-file-path=./models/primary/config.txt'
# tracker='nvtracker ll-lib-file=/opt/nvidia/deeepstream/deepstream-6.2/lib/libnvds_nvmultiobjecttracker.so tracker-width=640 tracker-height=384 ll-config-file=/workspace/custom_tracker.yml'
demuxer='nvstreamdemux name=demux demux.src_0'


# out_video=drawed_videos/video0.mkv
out_video=$2

rm ./result_video.jsonl
# gst-launch-1.0 -e filesrc location=${in_video} ! queue ! decodebin ! queue ! ${muxer} ! queue ! ${primary} ! queue ! ${demuxer} ! queue ! nvvideoconvert ! queue ! dsexample full-frame=0 ! queue ! nvdsosd ! queue ! nvvideoconvert ! queue ! nvv4l2h264enc ! h264parse ! mp4mux faststart=true ! filesink location=${out_video}
# gst-launch-1.0 -e filesrc location=${in_video} ! decodebin ! videoconvert ! queue ! ${muxer} ! queue ! ${primary} ! queue ! ${demuxer} ! queue ! nvvideoconvert ! queue ! dsexample full-frame=0 ! queue ! nvdsosd ! queue ! nvvideoconvert ! queue ! nvv4l2h264enc ! h264parse ! mp4mux faststart=true ! filesink location=${out_video}
gst-launch-1.0 -e filesrc location=${in_video} ! decodebin ! videoconvert ! nvvideoconvert ! ${muxer} ! ${primary} ! ${demuxer} ! dsexample full-frame=0 ! nvvideoconvert ! nvdsosd ! nvvideoconvert ! x264enc ! h264parse config-interval=1 ! mp4mux faststart=true ! filesink location=${out_video} 
# ffmpeg -i ./temp.mp4 -c:v libx264 -preset fast -b:v 8000k -maxrate 8000k -bufsize 16000k -g 25 -movflags +faststart -vf "setpts=PTS-STARTPTS" -af "asetpts=PTS-STARTPTS" ${out_video}

