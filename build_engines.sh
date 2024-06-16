if [ ! -f /workspace/models/primary/model.onnx_b1_gpu0_fp16.engine ]; then
    /usr/src/tensorrt/bin/trtexec --onnx=/workspace/models/primary/model.onnx --saveEngine=/workspace/models/primary/model.onnx_b1_gpu0_fp16.engine --fp16
fi