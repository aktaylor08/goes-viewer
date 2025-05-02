#!/usr/bin/env python3
import datetime
import sys

import redis
import re

import boto3
from botocore import UNSIGNED
from botocore.client import Config

def find_data(lookback: int):
    client = redis.Redis()
    s3 = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
    start_time = datetime.datetime.now(datetime.UTC)
    start_prefix = start_time.strftime("ABI-L1b-RadF/%Y/%j/%H/OR_ABI-L1b-RadF-M6C02")    
    atime = start_time - datetime.timedelta(minutes=lookback)
    time_limit = atime
    prefix = atime.strftime("ABI-L1b-RadF/%Y/%j/%H/OR_ABI-L1b-RadF-M6C02")
    while True:
        bucket = s3.Bucket("noaa-goes19")
        ch2 = list(bucket.objects.filter(Prefix=prefix))
        for x in ch2:
            f = re.search('.*ABI.*s(\d\d\d\d)(\d\d\d)(\d\d)(\d\d).*', x.key)
            shot_time = datetime.datetime(year=int(f.group(1)), month=1, day=1, tzinfo=datetime.UTC) + datetime.timedelta(days=int(f.group(2)) -1, hours=int(f.group(3)), minutes=int(f.group(4)))
            if shot_time >= time_limit:
                client.sadd('totile', x.key)
        if prefix == start_prefix:
            break
        atime = atime + datetime.timedelta(hours=1)
        prefix = atime.strftime("ABI-L1b-RadF/%Y/%j/%H/OR_ABI-L1b-RadF-M6C02")

def main():
    if len(sys.argv) > 1:
        lookback = int(sys.argv[1])
    else:
        lookback=60
    find_data(lookback)

if __name__ == "__main__":
    main()
