import hashlib
import os
import sys
import time
import uuid
import json
import logging
import requests
import subprocess
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

# ==== 配置项 ====
EMAIL = "1499405887@qq.com"
PASSWORD = "2c654e5020adb124f9f34e2963308737"
REGION = "CN"
UUID = "launch-master-py-auto"
LOGIN_URL = f"https://api-test-cn.aosulife.com/v1/user/login?uuid={UUID}&t={int(time.time())}"
STS_URL = f"https://api-test-cn.aosulife.com/v1/sts/getPlayInfo?uuid={UUID}&t={int(time.time())}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "log/viewer")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")


def login():
    timestamp_ms = int(time.time() * 1000)
    gz_uuid = uuid.uuid4()

    payload = {
        "countryAbbr": "CN",
        "countryCode": "86",
        "email": EMAIL,
        "password": PASSWORD,
        "region": REGION,
        "type": "1"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Gz-Pid": "glazero",
        "Gz-Sign": "309a2e34497e5da0f892bc754c8fb2d9",
        "Gz-Imei": "b7235aaeb830185c"
    }
    resp = requests.post(LOGIN_URL, headers=headers, data=payload, verify=False)
    data = resp.json().get("data", {})
    sid = data.get("sid")
    uid = data.get("uid")
    if not sid or not uid:
        logging.error("登录失败，sid 获取失败")
        sys.exit(1)
    return sid, uid


print(login())
