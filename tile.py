#!/usr/bin/env python3
import datetime
import sys
from pathlib import Path

import xarray
import numpy as np
import redis
import time
import io


import boto3
from botocore import UNSIGNED
from botocore.client import Config

from PIL import Image

def download_data():
    print("DOWNLOADING NEW DATA")
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    atime = datetime.datetime.now(datetime.UTC)
    while True:
        bucket = s3.Bucket("noaa-goes19")
        prefix = atime.strftime("ABI-L1b-RadF/%Y/%j/%H/OR_ABI-L1b-RadF-M6C02")
        ch2 = list(bucket.objects.filter(Prefix=prefix))
        if ch2:
            last_file_key = ch2[-1]
            print("Downloading", last_file_key)
            bucket.download_file(last_file_key.key, "latest-conus.nc")
            break
        else:
            atime = atime - datetime.timedelta(hours=1)
            print("going back an hour")

class Tiler:

    def __init__(self, file: str | Path):
        self.file = Path(file)
        self.full_res = 21696
        self.max_res = 32768 
        self.min_window = -0.151865
        self.max_window = 0.151865
        self.step = 1.40070915e-05
        self.tile_size =  256
        self.sat_height =  35786023
        self.tile_set_points = self.step *  self.max_res + self.min_window
        self.r_client = redis.Redis()
        print((self.max_res / 256) * self.sat_height)

    def make_images(self, level, images, ds):
        key_start = f"{time.strftime("%Y-%m-%dT%H-%M-%S",time.gmtime(ds.t.values.astype(int)/1000000000))}:vis:{level}"
        pix_per_img = int(self.max_res / images)
        img_step = int(pix_per_img / self.tile_size)
        for imgx in range(images):
            for imgy in range(images):
                start_x = imgx * pix_per_img
                start_y = imgy * pix_per_img
                end_x = start_x + pix_per_img
                end_y = start_y + pix_per_img
                if start_y > ds.y.shape[0] or start_x > ds.x.shape[0]:
                    print("skip")
                    continue
                values = ds.Rad[start_y:end_y:img_step, start_x:end_x:img_step] * ds.kappa0 * 256
                new_values = values.data.astype(np.uint8)
                if values.data.shape != (256, 256):
                    dshape = np.array(values.data.shape)
                    needed = np.array([256, 256]) - dshape
                    pad_width = [(0, x) for x in needed] 
                    new_values = np.pad(new_values, pad_width)
                image = Image.fromarray(new_values, mode="L")
                dabytes = io.BytesIO()
                image.save(dabytes, 'png')
                rkey = f"{key_start}:{imgx}:{imgy}"
                self.r_client.set(rkey, dabytes.getvalue())
                print(f"Saved to {rkey}")

    def tile(self):
        ds = xarray.open_dataset("latest-conus.nc")
        tileset_key = f"{time.strftime("%Y-%m-%dT%H-%M-%S",time.gmtime(ds.t.values.astype(int)/1000000000))}"
        level = 0
        images = 1
        total_points_dim = images * self.tile_size
        while total_points_dim  < self.full_res:
            self.make_images(level, images, ds)
            level += 1
            images *= 2
            total_points_dim = images * self.tile_size
        self.make_images(level, images, ds)
        self.r_client.sadd("obs:vis", tileset_key.encode("UTF-8"))
        print(self.r_client.smembers("obs:vis"))

def redis_loop():
    client = redis.Redis()
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    bucket = s3.Bucket("noaa-goes19")
    for x in client.sdiff('totile', 'tiledone'):
        bucket.download_file(x.decode(), "latest-conus.nc")
        worker = Tiler("latest-conus.nc")
        worker.tile()
        client.sadd('tiledone', x)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('r'):
            redis_loop()
        else:
            download_data()
            worker = Tiler("latest-conus.nc")
            worker.tile()

if __name__ == "__main__":
    main()
