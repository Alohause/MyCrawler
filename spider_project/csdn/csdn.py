# csdn.py
from selenium import webdriver
import os
import time
import html2text as ht
from bs4 import BeautifulSoup
import parsel
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# html模板，主要是为了设置<meta charset="UTF-8">来解决乱码问题
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    {content}
</body>
</html>"""

# md文件存储路径
path = "./文件"


# 初始化浏览器
def init():
    # 实现无可视化界面的操作
    chrome_options = Options()
    # 移除headless模式以便更好地调试
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 实施规避检测
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # 设置ChromeDriver路径
    chromedriver_path = "D:/pythonProject/爬虫/spider_project/chromedriver.exe"
    service = Service(executable_path=chromedriver_path)

    # 创建驱动实例，传入service和options参数
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 执行CDP命令来规避检测
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            delete navigator.__proto__.webdriver;
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
        '''
    })

    # 请求CSDN
    driver.get("https://www.csdn.net/")
    time.sleep(3)  # 增加等待时间确保页面加载

    # 操控浏览器滑轮滑到底部
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2)

    # 继续操控浏览器滑轮进行逐步滑动
    # 如果想要爬取更多文章，可控制滑轮向下多滑
    for y in range(15):  # 增加滑动次数
        # 0,300  每次滑动300像素
        js = 'window.scrollBy(0,300)'
        driver.execute_script(js)
        time.sleep(1)  # 增加等待时间

    time.sleep(5)  # 增加总等待时间
    # 返回driver
    return driver

# 爬取
def Crawling(driver):
    # 使用lxml库解析
    data = BeautifulSoup(driver.page_source, "lxml")

    # 查找文章列表容器
    feed_container = None
    # 尝试查找首页文章区域容器
    possible_containers = [
        "home-article",
        "home-content-box",
        "home_box_left",
        "feedlist_mod home",
        "container clearfix",
        "main"
    ]

    for container_class in possible_containers:
        feed_container = data.find(class_=container_class)
        if feed_container:
            print(f"找到文章容器: {container_class}")
            break

    # 查找文章项
    li_list = []
    if feed_container:
        # 尝试多种文章项选择器，按优先级排序
        selectors = [
            "article",  # 最新CSDN可能直接使用article标签
            "div[class*='article']",  # 包含article的class
            ".article--item",
            ".article-item-box",
            ".clearfix",
            "[data-type='blog']",  # CSDN特定属性
            "li"  # 最后尝试li标签
        ]

        for selector in selectors:
            if selector.startswith('.'):
                li_list = feed_container.find_all(class_=selector[1:])
            elif selector.startswith('['):
                li_list = feed_container.find_all(attrs={selector.split('[')[1].split('=')[0]: selector.split('=')[1][:-1]})
            elif selector == "article":
                li_list = feed_container.find_all("article")
            else:
                li_list = feed_container.find_all(selector)

            if li_list:
                print(f"使用选择器 '{selector}' 找到 {len(li_list)} 篇文章")
                break
    else:
        # 如果没找到容器，直接在整个页面查找
        li_list = data.find_all("article")
        if not li_list:
            li_list = data.find_all(class_="article--item")
        if not li_list:
            li_list = data.find_all(class_="article-item-box")

    if not li_list:
        print("未能找到任何文章项")
        # 打印部分页面源码用于调试
        print("页面源码片段:")
        print(driver.page_source[:2000])
        return

    print(f"总共找到 {len(li_list)} 篇文章")

    # 遍历li_list
    article_count = 0
    for li in li_list:
        li_data = BeautifulSoup(str(li), "lxml")

        # 异常处理，对于有的没有详情页url的那肯定不是博客文章，直接continue
        try:
            # 查找文章链接，优先查找具有明确标识的链接
            page_url = None

            # 尝试多种方式获取链接
            # 1. 查找包含文章标题的链接
            title_links = li_data.find_all("a")
            for link in title_links:
                href = link.get("href")
                if href and "article/details" in href:
                    page_url = href
                    break

            # 2. 如果没找到，尝试第一个链接
            if not page_url and title_links:
                for link in title_links:
                    href = link.get("href")
                    if href and href.startswith("http") and "csdn" in href:
                        page_url = href
                        break

            # 3. 最后尝试任意链接
            if not page_url and title_links:
                page_url = title_links[0].get("href")

            if not page_url:
                continue

            # 确保是完整URL
            if page_url.startswith("//"):
                page_url = "https:" + page_url
            elif page_url.startswith("/"):
                page_url = "https://blog.csdn.net" + page_url

        except Exception as e:
            print(f"获取链接时出错: {e}")
            continue

        # 文章标题 - 优先查找h2,h3,h4等标题标签
        title = "无标题"
        title_elem = None

        # 查找标题元素
        for tag in ["h2", "h3", "h4", "h5"]:
            elems = li_data.find_all(tag)
            for elem in elems:
                links = elem.find_all("a")
                for link in links:
                    if link.get("href") == page_url or "article/details" in (link.get("href") or ""):
                        title_elem = link
                        break
                if title_elem:
                    break
            if title_elem:
                break

        # 如果还没找到，尝试直接从链接文本获取
        if not title_elem:
            links = li_data.find_all("a")
            for link in links:
                href = link.get("href")
                if href and (href == page_url or "article/details" in href):
                    title_elem = link
                    break

        if title_elem:
            title = title_elem.text.strip()

        # 过滤无效标题
        if not title or len(title) == 0 or title == "无标题" or len(title) < 2:
            # 尝试从其他地方获取标题
            title_div = li_data.find(class_="title")
            if title_div:
                title = title_div.text.strip()
            if not title or len(title) == 0 or title == "无标题" or len(title) < 2:
                continue

        # 进行详情页请求爬取
        try:
            page_Crawling(title, page_url, driver)
            article_count += 1
            print(f"第 {article_count} 篇文章: {title}")
            print("-" * 50)

            # 控制爬取速度
            time.sleep(2)
        except Exception as e:
            print(f"爬取文章 '{title}' 时出错: {e}")
            continue

    print(f"总共爬取了 {article_count} 篇文章")


# 详情页爬取并保存为md文件
def page_Crawling(title, page_url, driver):
    # 清理标题中的非法字符
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        title = title.replace(char, '_')

    if len(title) > 100:
        title = title[:100]

    if not os.path.exists(path):
        os.makedirs(path)

    print(f"正在访问: {page_url}")
    driver.get(page_url)
    time.sleep(3)

    # 懒加载
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight/3)")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight/2)")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2)

    # 选择器
    selector = parsel.Selector(driver.page_source)

    text = selector.css("article.baidu_pl").get()
    if not text:
        text = selector.css("article").get()
    if not text:
        text = selector.css(".article_content").get()
    if not text:
        text = selector.css(".blog-content-box").get()
    if not text:
        text = selector.css(".content").get()
    if not text:
        text = selector.css(".htmledit_views").get()
    if not text:
        text = selector.css(".markdown_views").get()

    # 获取整个body
    if not text:
        text = selector.css("body").get()

    with open("text.html", "w", encoding="utf-8") as f:
        # 需要设置html模板，不然出现乱码
        f.write(html.format(content=text or "内容获取失败"))

    text_maker = ht.HTML2Text()
    text_maker.ignore_links = False
    text_maker.body_width = 0  # 不自动换行

    # 读取html格式文件
    with open('text.html', 'r', encoding='UTF-8') as f:
        htmlpage = f.read()

    # 处理html格式文件中的内容
    text = text_maker.handle(htmlpage)

    # 写入处理后的内容
    with open(path + "/" + title + '.md', 'w', encoding="utf-8") as f:
        f.write(text)

    print(title + " 爬取完毕")


# 开始
if __name__ == "__main__":
    # 初始化
    driver = init()
    try:
        # 爬取
        Crawling(driver)
    finally:
        # 确保浏览器关闭
        driver.quit()
