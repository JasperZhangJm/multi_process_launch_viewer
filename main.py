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
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


# ==== 配置项 ====
EMAIL = "1499405887@qq.com"
PASSWORD = "Qwe222222"
REGION = "CN"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "log/viewer")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")

os.makedirs(LOG_DIR, exist_ok=True)

# ==== 日志配置 ====
logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def hash_md5(passwd: str) -> str:
    try:
        return hashlib.md5(passwd.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error encoding passwd: {e}")
        return ""


def login():
    timestamp_ms = int(time.time() * 1000)
    gz_uuid = uuid.uuid4()
    url = f"https://api-test-cn.aosulife.com/v1/user/login?uuid={gz_uuid}&t={timestamp_ms}"

    pwd_md5 = hash_md5(PASSWORD)

    payload = {
        "countryAbbr": "CN",
        "countryCode": "86",
        "email": EMAIL,
        "password": pwd_md5,
        "region": REGION,
        "type": "1"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Gz-Pid": "glazero",
        "Gz-Sign": "309a2e34497e5da0f892bc754c8fb2d9",
        "Gz-Imei": "b7235aaeb830185c"
    }

    try:
        resp = requests.post(url=url, headers=headers, data=payload, verify=False)
        resp.raise_for_status()

        data = resp.json().get("data", {})

        sid = data.get("sid")
        uid = data.get("uid")

        return sid, uid

    except requests.RequestException as e:
        logger.error(f'Request failed: {e}')

    return None


def get_sts(sid, uid, sns):
    timestamp_ms = int(time.time() * 1000)
    gz_uuid = uuid.uuid4()
    url = f"https://api-test-cn.aosulife.com/v1/sts/getPlayInfo?uuid={gz_uuid}&t={timestamp_ms}"

    payload: Dict[str, Union[str, List[str]]] = {"refresh": "true"}
    for sn in sns:
        payload.setdefault("sn[]", []).append(sn)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Gz-Sid": sid,
        "Gz-Uid": uid,
        "Gz-Pid": "glazero",
        "Gz-Sign": "309a2e34497e5da0f892bc754c8fb2d9",
        "Gz-Imei": "b7235aaeb830185c"
    }

    try:
        resp = requests.post(url=url, headers=headers, data=payload, verify=False)
        resp.raise_for_status()

        data = resp.json().get("data", {})

        ak = data.get("ak")
        sk = data.get("sk")
        token = data.get("token")

        return ak, sk, token
    except requests.RequestException as e:
        logger.error(f'Request Failed: {e}')

    return None


def start_viewer(channel, index, ak, sk, token):
    ts = time.strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOG_DIR, f"viewer_{channel}_{index}_{ts}.log")
    cmd = [
        "nohup", "./samples/kvsWebrtcClientViewer", channel
    ]

    env = os.environ.copy()
    env.update({
        "AWS_ACCESS_KEY_ID": ak,
        "AWS_SECRET_ACCESS_KEY": sk,
        "AWS_SESSION_TOKEN": token,
        "AWS_DEFAULT_REGION": "cn-north-1",
        "AWS_KVS_LOG_LEVEL": "1",
        "DEBUG_LOG_SDP": "TRUE"
    })

    try:
        with open(log_file, "w") as f:
            subprocess.Popen(cmd, cwd="build", stdout=f, stderr=subprocess.STDOUT, env=env)
        print(f"✅ viewer 启动完成: channel={channel} index={index}")
    except Exception as e:
        logging.error(f"❌ Failed: {channel} index={index} - {e}")


def load_tasks(channel_sn_file, viewers_per_channel):
    tasks = []
    sns = []
    with open(channel_sn_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                channel, sn = parts
                sns.append(sn)
                for i in range(1, viewers_per_channel + 1):
                    tasks.append((channel, str(i)))
    return tasks, sns


def main():
    channel_sn_file = os.path.join(BASE_DIR, "channel_sn.txt")
    if not os.path.exists(channel_sn_file):
        print("❌ 未找到 channel_sn.txt")
        sys.exit(1)

    viewers_per_channel = 5  # 可调节每个频道 viewer 数量
    tasks, sns = load_tasks(channel_sn_file, viewers_per_channel)
    sid, uid = login()
    ak, sk, token = get_sts(sid, uid, sns)

    print("🚀 开始启动 viewer...")
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(start_viewer, channel, index, ak, sk, token) for channel, index in tasks]
        for future in futures:
            future.result()

    print(f"🎉 所有 viewer 启动完成，总耗时：{int((time.time() - start_time) * 1000)}ms")


if __name__ == "__main__":
    main()
