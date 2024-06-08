#include <cstring>
#include <iostream>
#include "nvdsinfer_custom_impl.h"

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define CLIP(a,min,max) (MAX(MIN(a, max), min))

extern "C"
bool NvDsInferParseCustomYolov10 (std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
        NvDsInferNetworkInfo  const &networkInfo,
        NvDsInferParseDetectionParams const &detectionParams,
        std::vector<NvDsInferObjectDetectionInfo> &objectList);

extern "C"
bool NvDsInferParseCustomYolov10 (std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
        NvDsInferNetworkInfo  const &networkInfo,
        NvDsInferParseDetectionParams const &detectionParams,
        std::vector<NvDsInferObjectDetectionInfo> &objectList)
{
  static NvDsInferDims bboxLayerDims;
  static int bboxLayerIndex = -1;

  /* Find the bbox layer */
  if (bboxLayerIndex == -1) {
    for (unsigned int i = 0; i < outputLayersInfo.size(); i++) {
      if (strcmp(outputLayersInfo[i].layerName, "output0") == 0) {
        bboxLayerIndex = i;
        bboxLayerDims = outputLayersInfo[i].inferDims;
        break;
      }
    }
    if (bboxLayerIndex == -1) {
    std::cerr << "Could not find bbox layer buffer while parsing" << std::endl;
    return false;
    }
  }

  int numBoxesToParse = bboxLayerDims.d[1];

  float *outputBboxBuf = (float *) outputLayersInfo[bboxLayerIndex].buffer;

  for (int b = 0; b < numBoxesToParse; b++)
  {

    NvDsInferObjectDetectionInfo object;
    float rectX1f, rectY1f, rectX2f, rectY2f, rectWf, rectHf;

    float *outputX1 = outputBboxBuf + (b * 6);
    float *outputY1 = outputX1 + 1;
    float *outputX2 = outputY1 + 1;
    float *outputY2 = outputX2 + 1;

    float *outputScore = outputY2 + 1;
    float *outputClassId = outputScore + 1;

    rectX1f = outputX1[0];
    rectY1f = outputY1[0];
    rectX2f = outputX2[0];
    rectY2f = outputY2[0];

    rectWf = rectX2f - rectX1f;
    rectHf = rectY2f - rectY1f;

    object.detectionConfidence = outputScore[0];
    object.classId = outputClassId[0];

    object.left = rectX1f;
    object.top = rectY1f;
    object.width = rectWf;
    object.height = rectHf;

    objectList.push_back(object);

  }
  return true;
}

CHECK_CUSTOM_PARSE_FUNC_PROTOTYPE(NvDsInferParseCustomYolov10);