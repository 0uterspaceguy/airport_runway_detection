from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

import os
import uvicorn
import yaml


app = FastAPI()
# app.add_middleware(HTTPSRedirectMiddleware)

with open("/workspace/flet_app_config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get(path="/download/{filename}")
def main(filename: str):
    file_path = os.path.join(config["downloads_dir"], filename)
    if os.path.exists(file_path):
        video_file = open(file_path, mode="rb")
        return StreamingResponse(video_file, media_type="video/mp4")

        return FileResponse(path=file_path,
                            media_type="video/mp4",
                            headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=404, detail=f"{filename} not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=57777, log_level="info")