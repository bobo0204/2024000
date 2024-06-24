import requests
from bs4 import BeautifulSoup

def get_top_travel_titles(url, limit=5):
    """
    取得 ETtoday 旅遊雲指定網頁的前幾個標題

    :param url: 網頁URL
    :param limit: 要獲取的標題數量
    :return: 包含標題的列表
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
    except requests.RequestException as e:
        return f"無法取得網頁內容：{e}"

    # 使用 BeautifulSoup 解析 HTML 結構
    soup = BeautifulSoup(response.text, "html.parser")

    # 搜尋所有標題 (h3 標籤)
    titles = soup.find_all("h3", itemprop="headline", limit=limit)

    # 提取標題文字並返回
    return [title.text.strip() for title in titles]

# 測試函數
url = "https://travel.ettoday.net/category/%E6%A1%83%E5%9C%92/"
top_titles = get_top_travel_titles(url)

if isinstance(top_titles, str):
    # 如果返回的是錯誤信息
    result = top_titles
else:
    # 否則，返回標題列表
    result = "\n".join([f"{i}. {title}" for i, title in enumerate(top_titles, 1)])

# 返回結果
result
