import os
import re
import time
import json
import hashlib
import matplotlib
from urllib.parse import quote
import requests
from collections import Counter
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import csv

# 获取 w_rid 加密参数
def Getw_rid(wts, NextPage):
    l = [
        "mode=2",
        "oid=113503553787765",
        f"pagination_str={quote(NextPage)}",
        "plat=1",
        "seek_rpid=",
        "type=1",
        "web_location=1315875",
        f"wts={wts}"
    ]
    v = '&'.join(l)
    string = v + 'ea1db124af3c7062474693fa704f4ff8'
    MD5 = hashlib.md5()
    MD5.update(string.encode('utf-8'))
    return MD5.hexdigest()

# 发送请求
def GetResponse(url, data):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "Referer": "https://www.bilibili.com/video/BV1kRUWYPEU9/",
        "Cookie": "buvid3=30736EE2-A652-E843-8C7D-15FE334C093F14237infoc; b_nut=1735885814; _uuid=1010A8361E-B5DD-D5F10-5391-A783313E5561018656infoc; buvid_fp=425266f78c3c2f111610da9f9f5ae6e9; enable_web_push=DISABLE; buvid4=BBBD8F19-8486-37EB-4294-33462F13D3AC15545-025010306-nxcshLGrW5u1Uw0JyWmFjA%3D%3D; rpdid=|(u)YJklml)l0J'u~Jl))l)Jl; DedeUserID=412705110; DedeUserID__ckMd5=a21e4dc448f741eb; theme-tip-show=SHOWED; b_lsid=3CC91929_1985FD371EF; bsource=search_google; home_feed_column=4; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQyMTM1NTAsImlhdCI6MTc1Mzk1NDI5MCwicGx0IjotMX0.yjIXZHWrcswv4Ki6tXpnDM9Fe6pAd4ReU0EtzYCl3_Y; bili_ticket_expires=1754213490; SESSDATA=09bad035%2C1769506351%2Ccac98%2A71CjC67iLid2MGHy17K0ZJksdVKpveTZf4hurBEgyrY5N_xG894u8sGGDJIf-Hym0M1zQSVkotMFJMVUFrNXVaZURKZWdaZVlJRGN2cTFwdmFLQWVPMm0zd3Z5bm5ORy1NcmN5ZUhoeVJtdUFJM3BYNmhxN1RmLWIzVW4yandKOWhuakJ5TUY0Y2xRIIEC; bili_jct=a3da3c6928d5acd35de10ebd4943b463; theme-avatar-tip-show=SHOWED; bp_t_offset_412705110=1095714666232938496; browser_resolution=548-648; sid=5aa2tfax; CURRENT_FNVAL=4048; CURRENT_QUALITY=0",
    }
    return requests.get(url=url, params=data, headers=headers)

# 抓取 B 站评论（API方式）
def get_comments_from_bilibili(bv_id, max_pages=10):

    # 固定 oid（根据视频 BV 号获取）
    oid_map = {
        "BV1kRUWYPEU9": "113503553787765"
    }
    oid = oid_map.get(bv_id, "113503553787765")

    offset = '""'
    comments = []

    # CSV 文件写入
    f = open('bilibili_comments.csv', mode='w', encoding='utf-8-sig', newline='')
    csv_writer = csv.DictWriter(f, fieldnames=['昵称', '性别', '地区', '评论'])
    csv_writer.writeheader()

    for _ in range(max_pages):
        link = 'https://api.bilibili.com/x/v2/reply/wbi/main'
        pagination_str = '{"offset":%s}' % offset
        pagination_str2 = json.dumps(json.loads(pagination_str), separators=(',', ':'))
        wts = int(time.time())
        w_rid = Getw_rid(wts, pagination_str2)

        params = {
            'oid': oid,
            'type': '1',
            'mode': '2',
            'pagination_str': pagination_str,
            'plat': '1',
            'seek_rpid': '',
            'web_location': '1315875',
            'w_rid': w_rid,
            'wts': wts
        }

        response = GetResponse(link, params)
        if response.status_code != 200:
            print("请求失败，状态码：", response.status_code)
            break

        data = response.json()
        replies = data.get('data', {}).get('replies', [])
        if not replies:
            print("没有更多评论")
            print("Response data:", data)
            print("请求参数:", params)
            print("请求URL:", link)
            print("请求头:", GetResponse.__code__.co_consts)
            break

        for item in replies:
            member = item.get('member', {})
            content = item.get('content', {})
            location = item.get('reply_control', {}).get('location', '').replace('IP属地：', '')
            comment = {
                '昵称': member.get('uname', '未知'),
                '性别': member.get('sex', '未知'),
                '地区': location,
                '评论': content.get('message', '')
            }
            comments.append(comment['评论'])
            csv_writer.writerow(comment)

        cursor = data.get('data', {}).get('cursor', {})
        next_offset = cursor.get('pagination_reply', {}).get('next_offset')
        if not next_offset:
            break
        offset = json.dumps(next_offset)

    f.close()
    return comments

# 中文分词并去除停用词
def process_comments(comments, stopwords_path='stopwords.txt'):
    text = ' '.join(comments)
    text = re.sub(r'[0-9\W]+', ' ', text)
    words = jieba.cut(text)

    stopwords = set()
    if os.path.exists(stopwords_path):
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            stopwords = set(line.strip() for line in f)

    filtered_words = [w for w in words if w not in stopwords and len(w) > 1]
    return Counter(filtered_words)

# 生成词云图像
def generate_wordcloud(freq, out_path='wordcloud.png'):
    if not freq:
        print("没有可视化的词语，可能没有抓到评论。")
        return
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    wc = WordCloud(font_path=font_path, width=800, height=400, background_color='white')
    wc.generate_from_frequencies(freq)
    wc.to_file(out_path)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.title("Bilibili 评论词云", fontsize=16)
    plt.show()

# 主程序入口
if __name__ == '__main__':
    bv_id = 'BV1kRUWYPEU9'
    print("正在抓取评论...")
    comments = get_comments_from_bilibili(bv_id, max_pages=10)
    if comments:
        freq = process_comments(comments)
        print("正在生成词云...")
        generate_wordcloud(freq)
        print("词云生成完成！")
    else:
        print("未获取到任何评论，请检查网络、BV号是否正确或更换视频。")
