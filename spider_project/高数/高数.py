# 导入csv模块（保存数据）
import csv
# 导入哈希模块
import hashlib
import json
# 导入时间模块
import time
# 导入编码的方法
from urllib.parse import quote
# 导入数据请求模块
import requests
import random

def Getw_rid(wts, NextPage):
    # 获取加密参数的函数
    pagination_str = quote(NextPage)
    l = [
        "mode=2",
        "oid=48624233",
        f"pagination_str={pagination_str}",
        "plat=1",
        "seek_rpid=",
        "type=1",
        "web_location=1315875",
        f"wts={wts}"
    ]
    v = '&'.join(l)
    string = v + 'ea1db124af3c7062474693fa704f4ff8'  # 这行的 salt 可能已经过期
    print("[DEBUG] 待加密字符串:", string)

    MD5 = hashlib.md5()
    MD5.update(string.encode('utf-8'))
    w_rid = MD5.hexdigest()
    print("[DEBUG] 生成的 w_rid:", w_rid)

    return w_rid

def GetResponse(url, data):
    # 发送请求函数字：模拟浏览器#
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        'Referer':
            'https://www.bilibili.com/video/BV1Eb411u7Fw/?spm_id_from=333.337.search-card.all.click&vd_source=67e74457baeac20fb027ca0106d4b37d',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    }

    # 发送请求
    response = requests.get(url=url, params=data, headers=headers)
    return response

# 获取数据
def GetContent(offset=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/BV1Eb411u7Fw",
        "Cookie": " ",
    }

    # 请求参数
    oid = "48624233"
    pagination_str = quote(f'{{"offset":"{offset}"}}') if offset else ""
    ts = int(time.time())

    # 拼接签名前的字符串
    params_str = f"mode=2&oid={oid}&pagination_str={pagination_str}&plat=1&seek_rpid=&type=1&web_location=1315875&wts={ts}"
    print(f"[DEBUG] 待加密字符串: {params_str}")

    # 生成签名 w_rid（使用 md5 加密）
    import hashlib
    w_rid = hashlib.md5((params_str + "ea1db124af3c7062474693fa704f4ff8").encode("utf-8")).hexdigest()
    print(f"[DEBUG] 生成的 w_rid: {w_rid}")

    # 构造最终 URL
    url = f"https://api.bilibili.com/x/v2/reply/main?{params_str}&w_rid={w_rid}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 安全解析 JSON，防止非 JSON 返回导致崩溃
        try:
            JsonData = response.json()
        except requests.exceptions.JSONDecodeError:
            print("[ERROR] 返回内容无法解析为 JSON，可能被反爬。")
            return None

        # 判断是否被限制访问
        if JsonData.get("code") == -403:
            print("[ERROR] 被禁止访问，检查 w_rid、wts 或 Cookie 是否正确。")
            return None

        # 解析数据
        data = JsonData.get('data', {})
        if not data:
            print("[INFO] 没有获取到数据")
            return None

        replies = data.get('replies', [])
        if not replies:
            print("[INFO] 没有更多评论")
            return None

        print(f"[INFO] 本页共抓取到 {len(replies)} 条评论:")

        # 遍历并打印评论，格式化输出
        for i, item in enumerate(replies, 1):
            try:
                uname = item['member']['uname']
                sex = item['member']['sex']
                location = item['reply_control'].get('location', '').replace('IP属地：', '')
                message = item['content']['message']
                print(f"{i}. 昵称: {uname} | 性别: {sex} | 地区: {location}\n   评论: {message}\n")

                # 写入 CSV
                csv_writer.writerow({
                    '昵称': uname,
                    '性别': sex,
                    '地区': location,
                    '评论': message
                })

            except KeyError as e:
                print(f"[WARN] 数据缺失: {e}")
                continue

        # 获取下一页请求参数
        cursor = data.get('cursor', {})
        pagination_reply = cursor.get('pagination_reply', {})
        NextPage = pagination_reply.get('next_offset', None)

        if NextPage is None:
            print("[INFO] 已无更多评论")
            return None

        return NextPage

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 网络请求失败: {e}")
        return None
    finally:
        pass

if __name__ == "__main__":
    f = open('bdata4.csv', mode='w', encoding='utf-8-sig', newline='')
    csv_writer = csv.DictWriter(f, fieldnames=['昵称', '性别', '地区', '评论'])
    csv_writer.writeheader()
    offset = ""

    success_count = 0

    for page in range(1, 51):
        print(f"\n--- 正在抓取第{page}页 ---")
        result = GetContent(offset=offset)

        if result == "STOP":
            print("由于权限问题，停止继续抓取")
            break

        if result is None:
            print("数据抓取完成或遇到错误，停止抓取")
            break

        offset = result
        success_count += 1

        delay = random.uniform(1, 3)
        print(f"等待 {delay:.1f} 秒后继续...")
        time.sleep(delay)

    print(f"\n总共成功抓取 {success_count} 页数据")
    f.close()
