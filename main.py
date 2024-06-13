from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
import os
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get(path="/download/{filename}")
def main(filename: str):
    if os.path.exists(f"./download/{filename}"):
        return FileResponse(path=f"./download/{filename}",
                            headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=404, detail=f"{filename} not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=57777, log_level="info")