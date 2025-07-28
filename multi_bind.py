import hashlib
import time
import uuid
import requests
import argparse


# ==== 配置项 ====
EMAIL = "1499405887@qq.com"
PASSWORD = "Qwe222222"
REGION = "CN"
COMMON_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Gz-Pid": "glazero",
    "Gz-Sign": "309a2e34497e5da0f892bc754c8fb2d9",
    "Gz-Imei": "b7235aaeb830185c"
}


def hash_md5(passwd: str) -> str:
    try:
        return hashlib.md5(passwd.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error encoding passwd: {e}")
        return ""


# app
def login():
    gz_uuid = uuid.uuid4()
    timestamp_ms = int(time.time() * 1000)
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

    try:
        resp = requests.post(url=url, headers=COMMON_HEADERS, data=payload, verify=False)
        resp.raise_for_status()

        resp_json = resp.json()

        if resp_json.get("errno") != 0:
            print(f"❌ 接口失败，code={resp_json.get('code')}, msg={resp_json.get('errmsg')}")
            return None
        else:
            data = resp_json.get("data", {})
            sid = data.get("sid")
            uid = data.get("uid")

            return sid, uid

    except requests.RequestException as e:
        print(f'Request failed: {e}')
        if e.response is not None:
            print(f"服务端响应：{e.response.text}")

    return None


# app
def get_token(sid, uid):
    gz_uuid = uuid.uuid4()
    timestamp_ms = int(time.time() * 1000)
    url = f"https://api-test-cn.aosulife.com/v1/bind/getToken?uuid={gz_uuid}&t={timestamp_ms}"

    headers = {
        **COMMON_HEADERS,
        "Gz-Sid": sid,
        "Gz-Uid": uid
    }

    try:
        rsp = requests.post(url=url, headers=headers, timeout=(10, 10), verify=False)
        rsp.raise_for_status()

        data = rsp.json().get('data', {})
        token = data.get('token')
        if not token:
            print("❌ get_token失败，未获取到token")
            return None
        return token

    except requests.RequestException as e:
        print(f'Request Failed: {e}')
        if e.response is not None:
            print(f"服务端响应：{e.response.text}")

    return None


# firmware
def gz_bind(sn, token):
    gz_uuid = uuid.uuid4()
    timestamp_ms = int(time.time() * 1000)
    url = f"https://api-test-cn.fm.aosulife.com/v1/bind/bind?uuid={gz_uuid}&t={timestamp_ms}"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Gz-Pid": "glazero",
        "Gz-Sign": "99499e1677e666e61e285290b48b53ac"
    }
    payload = {
        "productId": "co36zjpraqsta5si",
        "sn": sn,
        "token": token
    }

    try:
        rsp = requests.post(url=url, headers=headers, data=payload, timeout=(10, 10), verify=False)
        rsp.raise_for_status()

        rsp_json = rsp.json()
        if rsp_json.get("errno") != 0:
            print(f"❌ SN: {sn} 绑定失败，msg: {rsp_json.get('errmsg')}")
        else:
            print(f"📌 绑定接口：✅ SN: {sn} 绑定成功")

    except requests.RequestException as e:
        print(f'Request Failed: {e}')
        if e.response is not None:
            print(f"服务端响应：{e.response.text}")

    return None


# app
def get_dev_list(sid, uid, sn):
    timestamp_ms = int(time.time() * 1000)
    gz_uuid = uuid.uuid4()
    url = f"https://api-test-cn.aosulife.com/v1/dev/getList?uuid={gz_uuid}&t={timestamp_ms}"

    headers = {
        **COMMON_HEADERS,
        "Gz-Sid": sid,
        "Gz-Uid": uid
    }

    try:
        rsp = requests.post(url=url, headers=headers, timeout=(10, 10), verify=False)
        rsp.raise_for_status()

        rsp_json = rsp.json()
        data = rsp_json.get("data", {})
        dev_list = data.get("list", [])
        if not isinstance(dev_list, list):
            print(f"❌ get_dev_list: 设备列表格式不正确，sn={sn}")
            return

        for dev in dev_list:
            if dev['sn'] == sn and dev['model'] == 'C2E2DA11' and dev['ori_model'] == 'C2E2DA11':
                print(f"[{time.strftime('%H:%M:%S')}] 📌 列表查询：✅ SN: {sn} 已出现在设备列表")
                break
        else:
            print(f"❌ 设备列表中没有查到{sn}")

    except requests.RequestException as e:
        print(f'Request Failed: {e}')
        if e.response is not None:
            print(f"服务端响应：{e.response.text}")

    return None


def parse_args():
    parser = argparse.ArgumentParser(description="批量绑定设备工具")
    parser.add_argument("--file", "-f", type=str, default="c2e_sn_list.txt", help="包含SN的稳步文件路径")
    return parser.parse_args()


def main():
    args = parse_args()
    sn_file = args.file

    login_result = login()
    if not login_result:
        print("❌ 登录失败")
        return
    sid, uid = login_result

    try:
        with open(sn_file, "r") as f_content:
            sns = [line.strip() for line in f_content if line.strip()]
    except FileNotFoundError:
        print(f"❌ 找不到 {sn_file} 文件")
        return

    failed_sns = []

    for i, sn in enumerate(sns, 1):
        print(f"\n🛠️ 正在处理第 {i}/{len(sns)} 个SN: {sn}")

        token = get_token(sid, uid)
        if not token:
            failed_sns.append(sn)
            print(f"❌ 未能获取token，跳过绑定 {sn}")
            continue

        gz_bind(sn, token)
        get_dev_list(sid, uid, sn)
        time.sleep(0.2)

    if failed_sns:
        print(f"\n⚠️ 共 {len(failed_sns)} 个 SN 绑定失败，可重试：")
        for sn in failed_sns:
            print(f" - {sn}")


if __name__ == "__main__":
    main()
