import configparser
import time
import re
import random
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_cookie_string(driver):
    cookies = driver.get_cookies()
    return '; '.join([f"{c['name']}={c['value']}" for c in cookies])

def get_company_id(url):
    match = re.search(r'/company/(\d+)', url)
    return match.group(1) if match else None

# # 司法案件
# def get_legal_case_data(company_id, cookie_str):
#     version_id = '6ab4940e-22175911-prod'
#     url = f"https://www.tianyancha.com/_next/data/{version_id}/company/{company_id}/sifa.json?cid={company_id}"

#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Cookie": cookie_str,
#         "Accept": "*/*",
#     }

#     try:
#         res = requests.get(url, headers=headers)
#         if res.status_code == 200:
#             data = res.json()
#             queries = data['pageProps']['dehydratedState']['queries']
#             for q in queries:
#                 try:
#                     case_data = q['state']['data']
#                     if isinstance(case_data, dict) and 'items' in case_data:
#                         for case in case_data['items']:
#                             print("案号:", case.get('caseNo', '无'))
#                             print("案由:", case.get('caseReason', '无'))
#                             print("法院:", case.get('court', '无'))
#                             print("日期:", case.get('date', '无'))
#                             print("案件身份:", case.get('role', '无'))
#                             print("-" * 40)
#                         return
#                 except:
#                     continue
#             print("未找到司法案件")
#     except Exception as e:
#         print(f"请求失败: {e}")

def run():
    service = Service(r'D:\pythonProject\爬虫\spider_project\天眼查\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })

    driver.get("https://www.tianyancha.com/")

    def check_for_captcha(driver):
        if "captcha" in driver.current_url.lower() or "验证" in driver.page_source:
            input("回车继续")
            return True
        return False

    check_for_captcha(driver)

    try:
        with open(r'D:\pythonProject\爬虫\spider_project\天眼查\cookies.json', 'r', encoding='utf-8') as f:
            cookies_config = json.load(f)

        for cookie_name, cookie_value in cookies_config['cookies'].items():
            cookie = {
                'name': cookie_name,
                'value': cookie_value,
                'domain': '.tianyancha.com',
                'path': '/'
            }
            driver.add_cookie(cookie)
        driver.refresh()
    except Exception as e:
        print(f"{e}")

    time.sleep(random.uniform(3, 8))

    company_name = "阿里巴巴"
    driver.get(f"https://www.tianyancha.com/nsearch?key={company_name}")
    check_for_captcha(driver)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    link = soup.find("a", class_="index_alink__zcia5 link-click")

    if link:
        result = {
            'text': link.text,
            'href': link.get("href")
        }
        print(f"{company_name}: {result['href']}")
        time.sleep(random.uniform(3, 8))
        driver.get(result['href'])

        # 获取参保人数
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        insurance_td = soup.find('td', string='参保人数')
        if insurance_td:
            insurance_count_td = insurance_td.find_next_sibling('td')
            if insurance_count_td and insurance_count_td.contents:
                first_content = insurance_count_td.contents[0]
                match = re.search(r'\d+', str(first_content))
                if match:
                    insurance_count = match.group()
                    print(f"参保人数: {insurance_count}")
                else:
                    print("未找到参保人数")

        # 获取 Cookie
        company_id = get_company_id(result['href'])
        cookie_str = get_cookie_string(driver)

        # 司法案件接口
        # if company_id:
        #     get_legal_case_data(company_id, cookie_str)
        # else:
        #     print("未能提取 company_id")

        # 税务评级
        def wait_for_table_rows(driver, min_rows=3, timeout=15):
            start = time.time()
            while time.time() - start < timeout:
                tax_div = driver.find_element(By.CSS_SELECTOR, "div[data-dim='taxCredit']")
                tax_table = tax_div.find_element(By.CLASS_NAME, "table-wrap")
                rows = tax_table.find_elements(By.TAG_NAME, "tr")
                if len(rows) >= min_rows:
                    return rows
                time.sleep(1)
            return rows
        try:
            time.sleep(5)
            # 直接查找税务评级容器
            tax_div = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-dim='taxCredit']"))
            )
            tax_table = tax_div.find_element(By.CLASS_NAME, "table-wrap")
            rows = wait_for_table_rows(driver, min_rows=6, timeout=20)
            if len(rows) > 1:
                print(f"{company_name} 的税务评级信息：")
                for idx, row in enumerate(rows[1:], start=1):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 6:
                        seq = cols[0].text.strip() if cols[0].text else ""
                        year = cols[1].text.strip() if cols[1].text else ""
                        credit_level = cols[2].text.strip() if cols[2].text else ""
                        type_ = cols[3].text.strip() if cols[3].text else ""
                        taxpayer_id = cols[4].text.strip() if cols[4].text else ""
                        eval_unit = cols[5].text.strip() if cols[5].text else ""
                        print(
                            f"{year}, 信用级别:{credit_level}")
            else:
                print("未找到税务评级")
        except Exception as e:
            import traceback
            print("获取出错:", e)
            traceback.print_exc()

    else:
        print(f"未找到 {company_name}")

    time.sleep(50)

if __name__ == "__main__":
    run()
