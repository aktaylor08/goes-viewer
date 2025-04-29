from fastapi import FastAPI
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont
import io

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
    img = Image.new('L', (256, 256))
    drawer = ImageDraw.Draw(img)
    drawer.text((100, 100), f"{crs}: {z}, {x}. {y}", fill=256)
    dabytes = io.BytesIO()
    img.save(dabytes, 'png')
    return Response(content=dabytes.getvalue(), media_type="Image/png")
