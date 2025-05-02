from fastapi import FastAPI
from fastapi.responses import Response
import time

app = FastAPI()


@app.get("/")
async def root():
    return {"Yeet": "Skeet"}


@app.get(
    "/tiles/{crs}/{z}/{x}/{y}.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def img(crs: str, z: int, x: int, y: int):
    t1 = time.time()
    with open(f"tiles/{z}-{x}-{y}.png", "rb") as f:
        data = f.read()
        print(time.time() - t1)
        return Response(content=data, media_type="Image/png")
