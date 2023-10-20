from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


@app.get("/")
async def root():
    return {"Yeet": "Skeet"}


@app.get(
    "/img/0/{x}/{y}",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def img(x: int, y: int):
    with open(f"tiles/{x}-{y}.png", "rb") as f:
        data = f.read()
        return Response(content=data, media_type="Image/png")
