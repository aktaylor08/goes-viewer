#!/usr/bin/env python3
import datetime
import matplotlib.pyplot as plt

import xarray
import numpy as np


import boto3
from botocore import UNSIGNED
from botocore.client import Config

from PIL import Image


def main():
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    print(start_time)
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    bucket = s3.Bucket("noaa-goes19")
    prefix = start_time.strftime("ABI-L1b-RadC/%Y/%j/%H/OR_ABI-L1b-RadC-M6C02")
    ch2 = bucket.objects.filter(Prefix=prefix)
    last_file = list(ch2)[-1]
    bucket.download_file(last_file.key, "latest-conus.nc")
    ds = xarray.open_dataset("latest-conus.nc")
    sizex = ds.x.shape[0]
    sizey = ds.y.shape[0]
    tilex = 512
    tiley = 512
    nx = ds.x.shape[0] // tilex
    ny = ds.y.shape[0] // tiley
    for x0 in range(nx + 1):
        xs = x0 * 512
        xe = (x0 + 1) * 512
        if xe > sizex:
            xe = sizex
        for y0 in range(ny + 1):
            ys = y0 * 512
            ye = (y0 + 1) * 512
            if ye > sizey:
                ye = sizey
            values = ds.Rad[ys:ye, xs:xe] * ds.kappa0 * 256
            image = Image.fromarray(values.data.astype(np.uint8), mode="L")
            image.save(f"tiles/{x0}-{y0}.png")


if __name__ == "__main__":
    main()
