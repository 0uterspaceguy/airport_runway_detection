from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
import os
import uvicorn
import yaml

app = FastAPI()

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
        return FileResponse(path=file_path,
                            headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=404, detail=f"{filename} not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=57777, log_level="info")