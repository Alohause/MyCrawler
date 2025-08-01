# 天眼查公司信息爬虫脚本

本项目使用 Selenium + BeautifulSoup 实现对 [天眼查](https://www.tianyancha.com) 网站的模拟浏览与信息提取，自动获取指定公司的**基本信息**、**参保人数**和**税务评级信息**。

> ⚠️ 本项目仅供学习与研究使用，禁止用于商业用途或违反天眼查使用条款的行为。

---

## 功能特点

- 自动打开天眼查首页并加载 Cookie
- 支持关键词搜索公司
- 自动跳转公司详情页
- 获取参保人数
- 获取税务评级（如有）
- 预留司法案件信息接口（已注释，可扩展）

---

## 环境依赖

- 确保你已安装以下 Python 库：`pip install selenium beautifulsoup4 requests`
- 还需下载对应版本的 Chrome 浏览器与 `chromedriver`，并确保路径正确设置。

---

## 项目结构

- **tianyancha_scraper.py** : 主爬虫脚本
- **cookies.json** : 登录后的 Cookie 文件（手动保存）
- **chromedriver.exe** : Chrome 驱动（与你的 Chrome 浏览器版本对应，文件中为138）

---

## 使用方法

### 1. 准备 Cookie 文件

1. 手动登录天眼查（使用 Chrome）
2. 导出登录后的 Cookie
3. 将其整理为如下格式保存为 `cookies.json`：

```json
{
  "cookies": {
    "token": "xxxxx",
    "auth_token": "xxxxx",
    "...": "xxxxx"
  }
}
```

### 2. 设置 chromedriver 路径

确保 `chromedriver.exe` 路径在脚本中设置正确：

`service = Service(r'_path_')`

或修改为相对路径：

`service = Service('./chromedriver.exe')`

### 3. 运行脚本

脚本将自动执行以下操作：

- 加载 Cookie 并刷新页面
- 搜索并打开公司页面（默认搜索“阿里巴巴”，可修改）
- 提取参保人数和税务评级
- 暂停 50 秒等待人工检查结果页面（可修改）

---

## 注意事项

* 网页加载速度受网络影响，建议保持延时 `time.sleep()`
* 天眼查有较强的反爬策略，请勿频繁请求
* 确保 Cookie 有效且为登录状态，否则无法访问公司信息页

---

## 许可证
本项目仅供学习研究，禁止用于非法用途。