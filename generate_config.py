# coding:utf-8
import configparser
import argparse

def parse_cookie_string(cookie_string: str) -> dict:
    cookies = {}
    parts = cookie_string.strip().split(';')
    for part in parts:
        if '=' not in part:
            print(f"警告：忽略无效 Cookie 片段：{part}")
            continue
        key, value = part.strip().split('=', 1)
        cookies[key.strip()] = value.strip()
    return cookies

def write_config_file(cookie_dict: dict, filename='config.ini'):
    config = configparser.ConfigParser()
    config['cookies'] = cookie_dict
    config['info'] = {
        'email': 'your_email@example.com',  # 用户需手动修改
        'password': 'your_password'
    }
    with open(filename, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f"成功生成 {filename}，包含 {len(cookie_dict)} 个 Cookie 项和默认账号信息！")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='将浏览器 Cookie 转换为 config.ini')
    parser.add_argument('--cookie', type=str, help='直接传入 Cookie 字符串')
    args = parser.parse_args()

    if args.cookie:
        raw_cookie = args.cookie
    else:
        print("请将从浏览器复制的 Cookie 粘贴到这里（粘贴整串 cookie 值）:")
        raw_cookie = input(">>> ").strip()

    if not raw_cookie:
        print("错误：输入为空！")
        exit(1)

    try:
        cookie_dict = parse_cookie_string(raw_cookie)
        write_config_file(cookie_dict)
    except Exception as e:
        print(f"发生错误：{e}")
