import time
import csv
import requests
from pyquery import PyQuery as pq

# 用户输入CSDN账号
account = input('请输入CSDN ID:')

# 构建基本的URL
baseUrl = f'https://{account}.blog.csdn.net'
myUrl = f'{baseUrl}/article/list/1'

# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# CSV 文件写入
f = open('csdn_articles.csv', mode='w', encoding='utf-8-sig', newline='')
csv_writer = csv.DictWriter(f, fieldnames=['标题', '日期', '阅读数', '评论数', '链接'])
csv_writer.writeheader()

try:
    # 测试连接是否正常
    response = requests.get(myUrl, headers=headers, timeout=10)
    response.raise_for_status()

    # 发送请求并获取页面内容
    myPage = response.text
    doc = pq(myPage)

    # 爬取文章列表
    page_num = 1
    total_articles = 0

    while True:
        myUrl = f'{baseUrl}/article/list/{page_num}'
        print(f'正在爬取第 {page_num} 页...')

        try:
            myPage = requests.get(myUrl, headers=headers, timeout=10)
            myPage.raise_for_status()
            myPage.encoding = 'utf-8'

            doc = pq(myPage.text)

            # 检查是否有文章列表
            articles = doc(".article-list .article-item")
            if not articles:
                articles = doc(".article-list > div")
            if not articles:
                print("没有更多文章了")
                break

            print(f'-----------------------------第 {page_num} 页---------------------------------')

            # 获取文章信息
            page_articles = 0
            for i, item in enumerate(articles.items()):
                title_elem = item("h4 a")
                if title_elem:
                    title = title_elem.text().strip()
                    # 过滤掉空标题或模板标题
                    if title and len(title) > 0 and not title.startswith("查看全文"):
                        # 获取文章链接
                        article_link = title_elem.attr("href")
                        if article_link and not article_link.startswith('http'):
                            article_link = 'https://blog.csdn.net' + article_link

                        # 日期获取
                        date_elem = item(".view-time-box")
                        if not date_elem:
                            date_elem = item(".date")
                        if not date_elem:
                            date_elem = item(".time")
                        if not date_elem:
                            date_elem = item("span:eq(0)")

                        date = date_elem.text() if date_elem else "未知日期"

                        # 获取阅读数和评论数
                        read_count = "阅读数未知"
                        comment_count = "评论数未知"

                        # 尝试不同的选择器获取阅读数和评论数
                        read_elems = item(".read-num")
                        if read_elems and read_elems.size() >= 1:
                            read_count = read_elems.eq(0).text()
                            if read_elems.size() >= 2:
                                comment_count = read_elems.eq(1).text()
                        else:
                            # 尝试其他可能的选择器
                            read_count_elem = item(".view-count")
                            comment_count_elem = item(".comment-count")

                            if read_count_elem:
                                read_count = read_count_elem.text()
                            if comment_count_elem:
                                comment_count = comment_count_elem.text()

                        print(f"{date} | {title} | {read_count} | {comment_count}")

                        # 写入CSV文件
                        csv_writer.writerow({
                            '标题': title,
                            '日期': date,
                            '阅读数': read_count,
                            '评论数': comment_count,
                            '链接': article_link
                        })

                        page_articles += 1
                        total_articles += 1

                        if article_link:
                            print(f"链接: {article_link}")
                        print("-" * 50)

            if page_articles == 0:
                print("本页没有有效文章，结束爬取")
                break

            page_num += 1
            time.sleep(1)  # 添加延时避免请求过快

        except requests.RequestException as e:
            print(f"获取页面失败: {e}")
            break

    print(f"总共爬取了 {total_articles} 篇文章")

except requests.RequestException as e:
    print(f"连接失败，请检查网络或CSDN ID是否正确: {e}")
finally:
    f.close()
    print("数据已保存到 csdn_articles.csv 文件中")
