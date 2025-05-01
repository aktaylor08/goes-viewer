from fastapi import FastAPI
from fastapi.responses import Response
import time
import redis

app = FastAPI()

r_client = redis.Redis()

latestkey = sorted(r_client.smembers('obs:vis'))[-1].decode("UTF-8")
print(latestkey)

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
    key = f"{latestkey}:vis:{z}:{x}:{y}"
    data = r_client.get(key) 
    print(time.time() - t1)
    return Response(content=data, media_type="Image/png")
