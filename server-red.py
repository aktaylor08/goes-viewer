from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import Response
import time
import redis

app = FastAPI()

r_client = redis.Redis()

latestkey = sorted(r_client.smembers('obs:vis'))[-1].decode("UTF-8")
origins = [
    "http://localhost",
    "http://localhost:8080",
    "file:///Users/adamtaylor/Projects/sat2/test.html",
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"Yeet": "Skeet"}


@app.get(
    "/tiles/{ob_time}/{z}/{x}/{y}.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def img(ob_time: str, z: int, x: int, y: int):
    if ob_time == 'latest':
        ob_time = latestkey
    t1 = time.time()
    key = f"{ob_time}:vis:{z}:{x}:{y}"
    data = r_client.get(key) 
    print(time.time() - t1)
    return Response(content=data, media_type="Image/png")


@app.get(
        "/obs/times/{type}",
        )
async def obs(type: str):
    data = [x.decode("UTF-8") for x in sorted(r_client.smembers(f'obs:{type}'), reverse=True)]
    return data 

